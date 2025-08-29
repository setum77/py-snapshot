# py-snapshot

**py-snapshot** - yтилита для Админов создающая скриншоты заданных рабочих станций по настраиваему интервалу.

Используется утилита `vncsnapshot` https://sourceforge.net/projects/vncsnapshot/

Создает zip-архивы и отправляет их по ftp.

Это мой учебный проект.

Эти задачи куда проще написать на bash, что я и сделал https://github.com/setum77/bash_snapshot
У меня есть решение на Python повторяющие решение на Bash состоящее из 2 файлов, но в этом проекте хотелось оформить как полноценный учебный проект на Python,
с использованием uv, json, logging, dotenv, schedule

## Возможности

- **Создание скриншотов** - по умолчанию скриншоты создаются и сохраняются в папке "~/py-snapshot-result/jpg/"

* **Интервал сканирования** - можно настроить в файле `.env` в минутах, если не указывать берется интервал в 3 мин.

- **Качество скриншотов** - vncsnapshot позволяет настроить качество снимков, опытным путем выставил наилучшие значения по соотношению размер-качество
- **Создание архивов** - архивы создаются раз в сутки в 00:30 в папке "~/py-snapshot-result/zip/"
- **Отправка по FTP** - после создания архива, архив отправляется на FTP сервер, можно не указывать, в этом случае архивы забирать любым другим способом
- **Хранение файлов** - в файле `.env` можно задать количество дней хранения файлов и архивов

* **Логирование** - весь процесс логируется

## Перспективы

- Управление через веб-интерфейс

- Настройка сканирования с выбором отделов организации, установкой расписания

- Подключении LLM API для более глубокого анализа эффективности работы сотрудников

- Построение отчетов и графиков работы отделов и конкретных сотрудников

## Требования:

- на рабочих станциях: установлен и запущен сервер VNC (предполагается пароль на всех рабочих станиция одинаковый)
- сервер, использовал Debian:
  - установлен Python, не ниже 3.9
  - установлен git

## Установка и запуск

1. **Установить vncsnapshot**

   ```bash
   sudo apt update
   sudo apt install vncsnapshot
   ```

2. **Создать зашифрованный файл с паролем от VNC сервера**

   - используется встроенная утилита создания паролей от vncsnapshot - vncpasswd

   * лучше перейти в домашнюю директориюв, в конфиг файле путь к паролю прописан от корневой папки

   ```bash
   cd ~
   vncpasswd
   ```

   - команда vncpasswd создаст (если ее еще нет) директорию .vnc и в ней файл passwd
   - нужно ввести пароль от VNC и подтверждение и так 2 раза

3. **Установить uv** - если не установлен

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

- `VNC_PASSWD_PATH=~/.vnc/passwd` - путь к файлу с паролем от VNC
- `FTP_SERVER` - адрес FTP сервера (если не заполнить, архивы будут храниться в `~/py-snapshot-result/zip)
- `FTP_USERNAME` - логин от FTP сервера
- `FTP_PASSWORD` - пароль от FTP сервера
- `FTP_REMOTE_PATH` - конечная папка на FTP сервере, для загрузки архивов
- `DAYS_TO_KEEP` - количество дней хранения файлов и архивов
- `TIME_INTERVAL` - интервал (в минутах) между сканированиями

11. **Редактируем и заполняем файл `data/computers.json`**

    ```bash
    nano src/vnc_snapshot/computers.json
    ```

12. **Запускать вручную**

```bash
uv run vnc-snapshot-scheduler
```

выключить комбинацией - Ctrl + C

13. **После отладки можно создать задание cron или сервис автозапуска**
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

14. **запустить сервис**

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

## Управление службой

**Отключить автозапуск**

- Даже если служба настроена как `WantedBy=multi-user.target`, можно отключить её автозапуск, сохранив возможность ручного управления:

```bash
sudo systemctl disable vnc-snapshot.service
```

**Запустить службу вручную**

- После отключения автозапуска ты всё ещё можешь запустить её вручную:

```bash
sudo systemctl start vnc-snapshot.service
```

**Остановка службы вручную**

```bash
sudo systemctl stop vnc-snapshot.service
```

**Перезапуск службы**

```bash
sudo systemctl restart vnc-snapshot.service
```

**Проверка статуса**

```bash
sudo systemctl status vnc-snapshot.service
```

**Просмотр логов**

```bash
sudo journalctl -u vnc-snapshot.service -f
```
