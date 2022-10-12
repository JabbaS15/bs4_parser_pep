# Проект парсинга PEP

## Используемые технологии
Python 3.10, BeautifulSoup

## Документация парсера
```
Парсер документации Python
positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера
optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
```

## Описание проекта
Парсер собирает иформацию сайта документации Python ```https://docs.python.org/3/``` и каталога с PEP'ми ```https://peps.python.org/```.

Парсера поддерживает 4 режима работы и 3 мода вывода результатов работы.

Режимы работы:
- ```whats-new```
- ```latest-version```
- ```download```
- ```pep```

Моды по выводу итогов парсинга:
- ```-o pretty``` - вывод результатов в консоль в виде таблицы;
- ```-o file``` - вывод результатов в виде **.csv** файла, который сохраняется в директорию ***/results***;
- без указания команды по выводу результатов, итоги выводтся в консоль в строчку.

Дополнительные опциональные аргументы можно узнать из Документации парсера или вызвать файл ```main.py``` c аргументом ```-h```.

Вся информация по парсингу пишется в логи, уровни **INFO** и **ERROR**.
RotatingFileHandler подчищает устаревшие логи: ```maxBytes=10 ** 6```, ```backupCount=5```.

---

Режим работы ```whats-new``` сканирует страницу ```https://docs.python.org/3/```, раздел ***"Docs by version"***, и собирает ссылки на каждую версию ***Python***. Далее сканирует карточку каждой версии ***Python*** и выводит информацию: ссылка на статью, заголовок, редактор, автор.

---

Режим работы ```download``` сканирует страницу ```https://docs.python.org/3/download.html``` и скачивает PDF-файл документации zip-архивом. Архив сохраняется в директорию ***/downloads***.

---

Режим работы ```pep``` сканирует страницу ```https://peps.python.org/```, собирает статусы всех **PEP**'ов, ссылки на каждый **PEP** и подсчитывает общее количество **PEP**'ов.

---

## Запуск проекта
1. Клонировать репозиторий:
```bash
git clone https://github.com/JabbaS15/bs4_parser_pep.git
```

2. Создать виртуальное окружение:
```bash
python3 -m venv venv
```

3. Активировать виртуальное окружение и установить зависимости из ```requirements.txt```:
```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

4. Запустить ```main.py``` и ознакомиться с документацией парсера:
```bash
python3 main.py -h
```
