

def setup_api_url():
    print("\n Настройка Events Provider API")
    print("Если у вас есть реальный API, введите его URL.")
    print("Если оставить пустым — будут использованы мок-данные (заглушки).\n")

    url = input("URL API (например, https://api.example.com): ").strip()

    if url:
        with open(".env", "w") as f:
            f.write(f"EVENTS_API_URL={url}\nAPI_MODE=real\n")
        print(f"\n API URL сохранён: {url}")
        print("   Приложение будет работать с реальным API.")
    else:
        with open(".env", "w") as f:
            f.write("API_MODE=mock\n")
        print("\n Выбран режим мок-данных (заглушки).")
        print("   Приложение будет использовать фейковые данные.")


if __name__ == "__main__":
    setup_api_url()
