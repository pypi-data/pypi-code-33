import os

platforms_list_upper = [
    "MCU",
    "Nrf52832",
    "Nrf52840",
    "Stm32f4",
    "Stm32f401",
    "Stm32f407",
    "Stm32f410",
    "Stm32f411",
    "Stm32f413",
    "Stm32f429",
    "Stm32f446",
    "Stm32l476",
    "Stm32l475",
    "Mk64fn1m0vll12",
]

platforms_list_lower = [
    "nrf52832",
    "nrf52840",
    "stm32f4",
    "stm32f401",
    "stm32f407",
    "stm32f410",
    "stm32f411",
    "stm32f413",
    "stm32f429",
    "stm32f446",
    "stm32l476",
    "stm32l475",
    "mk64fn1m0vll12",
]

folder_path = os.path.join(os.path.dirname(__file__), 'platforms', 'default-boards')
platforms_default_config_dict = {
    "nrf52832":     os.path.join(folder_path, "nrf52832_default_board.json"),
    "nrf52840":     os.path.join(folder_path, "nrf52840_default_board.json"),
    "stm32f4":      os.path.join(folder_path, "stm32f411_default_board.json"),
    "stm32f401":    os.path.join(folder_path, "stm32f401_default_board.json"),
    "stm32f407":    os.path.join(folder_path, "stm32f407_default_board.json"),
    "stm32f410":    os.path.join(folder_path, "stm32f410_default_board.json"),
    "stm32f411":    os.path.join(folder_path, "stm32f411_default_board.json"),
    "stm32f413":    os.path.join(folder_path, "stm32f413_default_board.json"),
    "stm32f429":    os.path.join(folder_path, "stm32f429_default_board.json"),
    "stm32f446":    os.path.join(folder_path, "stm32f446_default_board.json"),
    "stm32l476":    os.path.join(folder_path, "stm32l476_default_board.json"),
    "stm32l475":    os.path.join(folder_path, "stm32l475_default_board.json"),
    "mk64fn1m0vll12":  os.path.join(folder_path, "mk64fn1m0vll12_default_board.json")
}
