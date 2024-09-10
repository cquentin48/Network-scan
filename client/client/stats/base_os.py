from datetime import datetime
import psutil


class BaseOS:
    """
    Operating System virtual class
    """

    def __init__(self) -> None:
        raise NotImplementedError("Virtual class! Can't implement it!")

    def ram_usage(self) -> dict:
        """
        Get the system virtual memory statistics
        """
        memory = psutil.virtual_memory()._asdict()
        return self.__format_dict(memory)

    def __format_dict(self, raw_data: dict):
        """
        Format dictionnary with bytes inputs
        with the correct unit.

        :type raw_data: dict
        :param raw_data: Raw dictionnary with bytes units
        """
        formatted_data = {}
        for key, value in raw_data.items():
            formatted_data[key] = self.__format_value(value)
        return formatted_data

    def get_uptime(self) -> float:
        """
        Get the system uptime duration
        """
        current_timestamp = datetime.now().timestamp()
        return current_timestamp - psutil.boot_time()

    def __get_partitions(self):
        return psutil.disk_partitions()

    def get_disks_usage(self) -> dict:
        """
        Fetch the partitions disks usage statistics
        """
        partitions = self.__get_partitions()

        disks_stats = {}
        for partition in partitions:
            path = partition.mountpoint
            try:
                drive = psutil.disk_usage(path)
                raw_stats = {
                    'total': drive.total,
                    'used': drive.used,
                    'free': drive.free
                }
                disks_stats[path] = self.__format_dict(raw_stats)
                disks_stats[path]['type'] = partition.fstype
            except OSError:
                pass

        return disks_stats

    def __format_value(self, value) -> str:
        units = ['bytes', 'kB', 'MB', 'GB', 'TB']
        index = 0

        while value > 1024:
            value /= 1024
            index += 1

        return f"{value} {units[index]}"
