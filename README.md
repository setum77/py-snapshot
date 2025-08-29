# vnc-snapshot

**vnc-snapshot** - yтилита для Админов создающая скриншоты заданных рабочих станций каждые 3 мин.

Создает zip-архивы и отправляет их по ftp. Это мой учебный проект.

Эти задачи куда проще написать на bash, что я и сделал https://github.com/setum77/bash_snapshot
У меня есть скрипты на Python повторяющие Bash, но в этом проекте хотелось оформить как полноценный учебный проект на Python,
с использованием uv, json, logging, dotenv, schedule

## Возможности

- **Создание скриншотов** по умолчанию скриншоты создаются каждые 3 мин. и сохраняются в папке "~/py_snapshot"
- **Создание архивов** архивы создаются раз в сутки в 00:30 в папке "~/py_zip_snpsht/"
- **Отправка по FTP** после создания архива, архив отправляется на FTP сервер
- **Хранение файлов** в файле `.env` можно задать количество дней хранения файлов и архивов

## Требования:

- на рабочих станциях: установлен и запущен сервер VNC
- сервер, использовал Debian:
  - установлен Python
  - установлен git
  - используется утилита vncsnapshot https://sourceforge.net/projects/vncsnapshot/

## Установка и запуск

1. **Установить vncsnapshot**
   ```bash
   sudo apt update
   sudo apt install vncsnapshot
   ```
2. **Создать зашифрованный файл с паролем от VNC сервера**
   - лучше перейти в домашнюю директориюв, конфиг файле путь к паролю прописан от корневой папки
   ```bash
   cd ~
   vncpasswd
   ```
   - команда vncpasswd создаст (если ее еще нет) директорию .vnc и в ней файл passwd
   - запросит пароль и подтверждение
3. **Установить uv**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   - перезапустить shell или
   ```bash
   source $HOME/.local/bin/env
   ```
   - посмотреть версию uv
   ```bash
   uv --version
   ```
4. **Записать проект любым способом**
   - если через GitHub
   ```bash
   cd ~
   git clone https://github.com/Setum77/py-snapshot.git
   ```
5. **Перейти в созданную директорию**
   ```bash
   cd py-snapshot
   ```
6. **Создать виртуальное окружение и активировать**
   ```bash
   uv venv
   source .venv/bin/activate
   ```
7. **Установить зависимости**
   ```bash
   uv pip install -e .
   ```
8. **Копируем `.env.exemple` в `.env`**
   ```bash
   cp env.example .env
   ```
9. **Если в пункте 2 сохранили файл с паролем в другой папке, то открываем `.env` и редактируем путь `VNC_PASSWD_PATH`**
   ```bash
   nano .env
   ```
10. **Задаем другие параметры в файле `.env`**
11. **Редактируем и заполняем файл `data/computers.json`**
    ```bash
    nano src/vnc_snapshot/computers.json
    ```
12. **Создать задание cron или сервис автозапуска**
    - создать автозапуск
    ```bash
    sudo nano /etc/systemd/system/vnc-snapshot.service
    ```
    - вставить код, заменить `your-username` на свой

```ini
[Unit]
Description=VNC Snapshot Scheduler
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/py-snapshot
ExecStart=/home/your-username/py-snapshot/.venv/bin/vnc-snapshot-scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

12. **запустить сервис**

    - Перезагрузи systemd

    ```bash
    sudo systemctl daemon-reload
    ```

    - Включи автозапуск

    ```bash
    sudo systemctl enable vnc-snapshot.service
    ```

    - Запусти сервис

    ```bash
    sudo systemctl start vnc-snapshot.service
    ```

    - Проверь статус

    ```bash
    sudo systemctl status vnc-snapshot.service
    ```

    - Просмотр логов

    ```bash
    sudo journalctl -u vnc-snapshot.service -f
    ```
## Управление службой
   
   **Отключить автозапуск**
   Даже если служба настроена как `WantedBy=multi-user.target`, ты можешь отключить её автозапуск, сохранив возможность ручного управления:
   ```bash
   sudo systemctl disable vnc-snapshot-scheduler.service
   ```
   
   **Запустить службу вручную**
   После отключения автозапуска ты всё ещё можешь запустить её вручную:
   ```bash
   sudo systemctl start vnc-snapshot-scheduler.service
   ```
   
   **Остановка службы вручную**
   ```bash
   sudo systemctl stop vnc-snapshot-scheduler.service
   ```

   **Перезапуск службы**
   ```bash
   sudo systemctl restart vnc-snapshot-scheduler.service
   ```
   **Проверка статуса**
   ```bash
   sudo systemctl status vnc-snapshot-scheduler.service
   ```