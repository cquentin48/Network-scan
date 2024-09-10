import winreg
uwp_apps = []

registry_path = r"Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages"

try:
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path)
    for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
        try:
            # Récupération de la sous-clé
            sub_key_name = winreg.EnumKey(reg_key, i)
            sub_key = winreg.OpenKey(reg_key, sub_key_name)
            # Extraire le nom du package UWP
            uwp_apps.append(sub_key_name)
        except EnvironmentError:
            continue
        finally:
            winreg.CloseKey(sub_key)
    winreg.CloseKey(reg_key)
except EnvironmentError:
    pass

print(uwp_apps)