import subprocess
import re
import os
from datetime import datetime

SNAPSHOT_DIR = "/.snapshots"

def run_cmd(cmd, check=True):
    """
    Sistem komutlarını güvenli bir şekilde çalıştırır ve çıktısını döndürür.
    """
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else str(e), e.returncode
    except Exception as e:
        return "", str(e), -1

def is_btrfs():
    """
    Kök dizinin (/) dosya sisteminin btrfs olup olmadığını kontrol eder.
    """
    stdout, _, code = run_cmd(["findmnt", "/", "-n", "-o", "FSTYPE"], check=False)
    if code == 0 and stdout == "btrfs":
        return True
    return False

def ensure_snapshot_dir():
    """
    Snapshot dizininin var olmasını sağlar.
    """
    if not os.path.exists(SNAPSHOT_DIR):
        stdout, stderr, code = run_cmd(["mkdir", "-p", SNAPSHOT_DIR], check=False)
        return code == 0
    return True

def list_snapshots():
    """
    Sistemdeki mevcut anlık görüntüleri listeler.
    Çıktı formatı: [{'id': str, 'name': str, 'path': str, 'date': str}]
    """
    if not is_btrfs():
        return []
    
    ensure_snapshot_dir()
    
    # BTRFS subvolume listesini al
    stdout, stderr, code = run_cmd(["btrfs", "subvolume", "list", "/"], check=False)
    if code != 0:
        return []
        
    snapshots = []
    # Örnek satır: ID 258 gen 57 top level 5 path .snapshots/snapshot_2026-06-23_173000
    pattern = re.compile(r'ID (\d+) gen \d+ top level \d+ path (.+)')
    
    for line in stdout.split('\n'):
        match = pattern.search(line)
        if match:
            subvol_id = match.group(1)
            rel_path = match.group(2)
            
            # Sadece .snapshots/ altında olanları filtrele
            if rel_path.startswith(".snapshots/") or rel_path.startswith("@snapshots/"):
                name = os.path.basename(rel_path)
                full_path = os.path.join("/", rel_path)
                
                # Tarih ve saat bilgisini isminden çekmeye çalışalım
                # Format: snapshot_YYYY-MM-DD_HH-MM-SS_Aciklama
                date_str = "Bilinmeyen Tarih"
                name_parts = name.split('_')
                if len(name_parts) >= 3 and name_parts[0] == "snapshot":
                    try:
                        # YYYY-MM-DD_HH-MM-SS kısmını birleştir
                        raw_date = f"{name_parts[1]} {name_parts[2].replace('-', ':')}"
                        date_str = raw_date
                    except Exception:
                        pass
                
                snapshots.append({
                    "id": subvol_id,
                    "name": name,
                    "path": full_path,
                    "date": date_str
                })
                
    # En güncel snapshot en üstte olacak şekilde sırala
    snapshots.sort(key=lambda x: x['name'], reverse=True)
    return snapshots

def create_snapshot(description=""):
    """
    Kök dizinin yeni bir anlık görüntüsünü (snapshot) oluşturur.
    """
    if not is_btrfs():
        return False, "Sistem dosya yapısı BTRFS değil."
        
    ensure_snapshot_dir()
    
    # Dosya adı için zaman damgası oluştur
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    sanitized_desc = "".join([c if c.isalnum() or c in ('-', '_') else '_' for c in description]).strip()
    
    snapshot_name = f"snapshot_{timestamp}"
    if sanitized_desc:
        snapshot_name += f"_{sanitized_desc}"
        
    dest_path = os.path.join(SNAPSHOT_DIR, snapshot_name)
    
    # Komutu çalıştır: btrfs subvolume snapshot / /.snapshots/snapshot_name
    stdout, stderr, code = run_cmd(["btrfs", "subvolume", "snapshot", "/", dest_path], check=False)
    if code == 0:
        return True, f"Snapshot başarıyla oluşturuldu: {snapshot_name}"
    else:
        return False, f"Hata oluştu: {stderr}"

def delete_snapshot(path):
    """
    Belirtilen path'deki anlık görüntüyü siler.
    """
    if not is_btrfs():
        return False, "Sistem dosya yapısı BTRFS değil."
        
    # Güvenlik kontrolü: Yolun .snapshots içinde olduğundan emin ol
    if not path.startswith(SNAPSHOT_DIR + "/"):
        return False, "Güvenlik Engeli: Sadece yedekleme klasöründeki snapshotlar silinebilir."
        
    stdout, stderr, code = run_cmd(["btrfs", "subvolume", "delete", path], check=False)
    if code == 0:
        return True, "Snapshot başarıyla silindi."
    else:
        return False, f"Hata oluştu: {stderr}"

def restore_snapshot(subvol_id, path):
    """
    Belirtilen anlık görüntüyü geri yüklemek üzere önyükleyici için varsayılan (default) yapar.
    NOT: Bu işlem bir sonraki yeniden başlatmada (reboot) aktif olur.
    """
    if not is_btrfs():
        return False, "Sistem dosya yapısı BTRFS değil."
        
    # Güvenlik kontrolü: Yolun .snapshots içinde olduğundan emin ol
    if not path.startswith(SNAPSHOT_DIR + "/"):
        return False, "Güvenlik Engeli: Geçersiz snapshot yolu."
        
    # Varsayılan subvolume ayarla: btrfs subvolume set-default <id> /
    stdout, stderr, code = run_cmd(["btrfs", "subvolume", "set-default", str(subvol_id), "/"], check=False)
    if code == 0:
        return True, f"Snapshot varsayılan olarak ayarlandı. Değişikliklerin uygulanması için sistemi yeniden başlatın.\n\nYol: {path}\nSubvol ID: {subvol_id}"
    else:
        return False, f"Geri yükleme başarısız oldu: {stderr}"

def is_auto_backup_enabled():
    """
    Otomatik yedekleme zamanlayıcısının aktif olup olmadığını kontrol eder.
    """
    timer_path = "/etc/systemd/system/btrfs-autosnap.timer"
    if not os.path.exists(timer_path):
        return False
    
    # Zamanlayıcının etkin olup olmadığını kontrol et
    stdout, _, code = run_cmd(["systemctl", "is-enabled", "btrfs-autosnap.timer"], check=False)
    return code == 0 and "enabled" in stdout

def setup_auto_backup(enable):
    """
    Otomatik yedeklemeyi (2 saatte bir) kurar veya kaldırır.
    """
    service_path = "/etc/systemd/system/btrfs-autosnap.service"
    timer_path = "/etc/systemd/system/btrfs-autosnap.timer"
    
    if enable:
        service_content = """[Unit]
Description=DualCoreX Otomatik BTRFS Snapshot Servisi
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /home/yms/Masaüstü/pardus/1-BTRFS_Snapshot_Araci/btrfs_helper.py --auto
"""
        timer_content = """[Unit]
Description=DualCoreX 2 Saatte Bir BTRFS Snapshot Zamanlayicisi

[Timer]
OnBootSec=10min
OnUnitActiveSec=2h
Unit=btrfs-autosnap.service

[Install]
WantedBy=timers.target
"""
        try:
            with open(service_path, "w", encoding="utf-8") as f:
                f.write(service_content)
            with open(timer_path, "w", encoding="utf-8") as f:
                f.write(timer_content)
                
            # Systemd yenile ve etkinleştir
            run_cmd(["systemctl", "daemon-reload"])
            run_cmd(["systemctl", "enable", "btrfs-autosnap.timer"])
            stdout, stderr, code = run_cmd(["systemctl", "start", "btrfs-autosnap.timer"])
            if code == 0:
                return True, "Otomatik yedekleme (2 saatte bir) başarıyla aktifleştirildi."
            else:
                return False, f"Zamanlayıcı başlatılamadı: {stderr}"
        except Exception as e:
            return False, f"Dosya yazma hatası: {str(e)}"
    else:
        try:
            run_cmd(["systemctl", "stop", "btrfs-autosnap.timer"])
            run_cmd(["systemctl", "disable", "btrfs-autosnap.timer"])
            
            if os.path.exists(service_path):
                os.remove(service_path)
            if os.path.exists(timer_path):
                os.remove(timer_path)
                
            run_cmd(["systemctl", "daemon-reload"])
            return True, "Otomatik yedekleme devredışı bırakıldı."
        except Exception as e:
            return False, f"Kaldırma hatası: {str(e)}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        success, msg = create_snapshot("otomatik_yedek")
        print(msg)
        sys.exit(0 if success else 1)
