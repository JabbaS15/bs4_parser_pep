import logging
import re
from collections import Counter
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, MAIN_PEP_URL, \
    DOWNLOADS_URL, DOWNLOADS_DIR
from outputs import control_output
from exceptions import TextNotFoundException
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(
        soup,
        tag='section',
        attrs={'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        main_div,
        tag='div',
        attrs={'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        name='li',
        attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, tag='a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, tag='h1').text
        dl = find_tag(soup, tag='dl').text.replace('\n', ' ')
        results.append((version_link, h1, dl))
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(
        soup,
        tag='div',
        attrs={'class': 'sphinxsidebarwrapper'}
    )
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        error_msg = 'Искомое значение не обнаружено'
        logging.error(error_msg, stack_info=True)
        raise TextNotFoundException(error_msg)

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))

    return results


def download(session):
    response = get_response(session, DOWNLOADS_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, tag='div', attrs={'role': 'main'})
    table_tag = find_tag(main_tag, tag='table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        tag='a',
        attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(DOWNLOADS_URL, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    archive_path = DOWNLOADS_DIR / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    results = []
    response = get_response(session, MAIN_PEP_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    pep_section = find_tag(
        soup,
        tag='section',
        attrs={'id': 'numerical-index'}
    )
    pep_tbody = find_tag(pep_section, tag='tbody')
    pep_tr = pep_tbody.find_all('tr')
    for tr in tqdm(pep_tr):
        try:
            pep_status = find_tag(tr, 'td').text[1:]
            expected_status = EXPECTED_STATUS[pep_status]
            href = find_tag(tr, 'a')['href']
            pep_href = urljoin(MAIN_PEP_URL, href)
            response = get_response(session, pep_href)
            soup = BeautifulSoup(response.text, features='lxml')
            status = soup.find(text='Status').find_next('dd').text

            if status not in expected_status:
                logging.info(f'\n'
                             f'Несовпадающие статусы:\n'
                             f'{pep_href}\n'
                             f'Статус в карточке: {status}\n'
                             f'Ожидаемые статусы: {expected_status}\n')
            results.append(status)
        except KeyError:
            print(f'Статус - {pep_status} не найден!')
    counter = Counter(results)
    return (
            [('Статус', 'Количество')]
            + list(counter.items())
            + [('Total', len(pep_tr))])


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()

    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
