import os
import json
import time
import pyautogui
import pyperclip
import collections
from loguru import logger


pyautogui.FAILSAFE = True


class AutoGui:
    def __init__(self):
        self.jiansuo_buttom = './images/jiansuo.png'
        self.tiaozhuan_buttom = './images/tiaozhuan.png'
        self.jiansuolishi_buttom = './images/jiansuolishi.png'
        self.kong_buttom = './images/kong.png'

        time.sleep(2)

        self.jiansuo_pos = pyautogui.center(pyautogui.locateOnScreen(self.jiansuo_buttom, confidence=0.8))
        self.drag_start_pos = [self.jiansuo_pos[0], self.jiansuo_pos[1] + 100]
        self.input_pos = [self.jiansuo_pos[0], self.jiansuo_pos[1] - 100]

        self.jiansuolishi_pos = pyautogui.center(pyautogui.locateOnScreen(self.jiansuolishi_buttom, confidence=0.8))
        self.ip_select_pos = [self.jiansuolishi_pos[0] + 90, self.jiansuolishi_pos[1]]
        self.ip_pos = [self.ip_select_pos[0], self.ip_select_pos[1] + 50]

        self._select_ip()

    def _select_ip(self):
        pyautogui.moveTo(self.ip_select_pos, duration=0.2)
        pyautogui.click()
        pyautogui.moveTo(self.ip_pos, duration=0.2)
        pyautogui.click()

    def _input_sql(self, sql):
        pyperclip.copy(sql)

        pyautogui.moveTo(self.input_pos, duration=0.2)
        pyautogui.click()
        pyautogui.hotkey('ctrl', 'v')

    def _delete_sql(self):
        pyautogui.moveTo(self.input_pos, duration=0.2)
        pyautogui.tripleClick()
        pyautogui.press('delete')

    def _click_jiansuo(self):
        pyautogui.moveTo(self.jiansuo_pos, duration=0.2)
        pyautogui.click()
    
    def _get_result(self):
        pyautogui.moveTo(self.drag_start_pos, duration=0.2)
        tiaozhuan_pos = pyautogui.center(pyautogui.locateOnScreen(self.tiaozhuan_buttom, confidence=0.8))
        drag_end_pos = [tiaozhuan_pos[0] + 450, tiaozhuan_pos[1] - 45]
        pyautogui.dragTo(drag_end_pos, button='left', duration=1)
        pyautogui.hotkey('ctrl', 'c')
        result = pyperclip.paste()
        
        return result

    def _get_page_num(self):
        def parse_page_info(page_info):
            page_num = 0
            if '...' in page_info:
                page_info = page_info.split('...')[-1]
            if '页' in page_info:
                page_info = page_info.split('页')[-1]
            page_info = page_info.split('下')[0]
            # 只有1
            if len(page_info) == 1:
                page_num = 1
            # 只有12
            elif len(page_info) == 2:
                page_num = 2
            # 最大为100
            elif int(page_info[-3] + page_info[-2] + page_info[-1]) == 100:
                page_num = 100
            # 从0开始
            elif int(page_info[0]) < int(page_info[1]) < int(page_info[2]):
                # 最大为两位数
                if int(page_info[-2]) == 1:
                    page_num = int(page_info[-2]+page_info[-1])
                # 最大为一位数
                else:
                    page_num = int(page_info[-1])
            # 两位数开始，最大不为100
            else:
                page_num = int(page_info[-2]+page_info[-1])

            return page_num

        tiaozhuan_pos = pyautogui.center(pyautogui.locateOnScreen(self.tiaozhuan_buttom, confidence=0.8))
        page_start_pos = [self.jiansuo_pos[0], tiaozhuan_pos[1]]
        pyautogui.moveTo(page_start_pos, duration=0.2)
        page_end_pos = [tiaozhuan_pos[0] - 150, tiaozhuan_pos[1]]
        pyautogui.dragTo(page_end_pos, button='left', duration=1)
        pyautogui.hotkey('ctrl', 'c')

        page_info = pyperclip.paste()

        page_num = parse_page_info(page_info)

        return page_num

    def _check_kong(self):
        try:
            pyautogui.center(pyautogui.locateOnScreen(self.kong_buttom, confidence=0.8))
        except:
            return False
        else:
            return True

    def _next_page(self):
        tiaozhuan_pos = pyautogui.center(pyautogui.locateOnScreen(self.tiaozhuan_buttom, confidence=0.8))
        xiayiye_pos = [tiaozhuan_pos[0] - 180, tiaozhuan_pos[1]]
        pyautogui.moveTo(xiayiye_pos, duration=0.2)
        pyautogui.click()

    def is_processed(self, sql):
        first = sql.split('select')[-1].split(',count(*)')[0]
        second = sql.split('from')[-1].split('where')[0]
        third = sql.split('by')[-1]
        file_name = (first + '_' + second + '_' + third + '_' + '.json').replace(' ', '')

        if not os.path.exists('./results'):
            os.makedirs('./results')

        if file_name in os.listdir('./results'):
            return True
        else:
            return False

    def _parse_result(self, sql):
        tmp_dict = collections.defaultdict(list)
        for num, info in self.total_result.items():
            key_word = info[self.key_word]
            cont = info['cont']
            tmp_dict[key_word].append({
                'num': num,
                'cont': cont
            })

        parse_dict = dict()
        for key_word, info_list in tmp_dict.items():
            if len(info_list) > 1:
                parse_dict[key_word] = info_list
        
        if parse_dict:
            first = sql.split('select')[-1].split(',count(*)')[0]
            second = sql.split('from')[-1].split('where')[0]
            third = sql.split('by')[-1]
            save_path = os.path.join('./parses', first + '_' + second + '_' + third + '_' + '.json').replace(' ', '')
            with open(save_path, 'w', encoding='utf-8') as js:
                json.dump(parse_dict, js, indent=4, ensure_ascii=False)

    def run(self, sql):

        self._delete_sql()

        self.total_result = dict()
        self.key_word = sql.split('(')[-1].split(',')[0]
        num = 0

        self._input_sql(sql)
        self._click_jiansuo()

        time.sleep(0.5)

        if self._check_kong():
            return

        page_num = self._get_page_num()
        logger.info('page num: {}'.format(page_num))

        for i in range(page_num):
            if i != 0:
                self._next_page()

            while True:
                try:
                    pyautogui.center(pyautogui.locateOnScreen(self.tiaozhuan_buttom, confidence=0.8))
                except:
                    time.sleep(0.5)
                    continue
                else:
                    break

            result_info = self._get_result().split()
            result_clean = list()
            for idx, item in enumerate(result_info):
                if ':' in item:
                    continue
                if '-' in item and ':' in result_info[idx + 1]:
                    result_clean.append(item + '_' + result_info[idx + 1])
                    continue

                result_clean.append(item)

            for date, cont in zip(result_clean[::2], result_clean[1::2]):
                self.total_result[str(num)] = {
                    self.key_word: date,
                    'cont': cont
                }

                num += 1

        logger.info('total items: {}'.format(num))

        first = sql.split('select')[-1].split(',count(*)')[0]
        second = sql.split('from')[-1].split('where')[0]
        third = sql.split('by')[-1]

        save_path = os.path.join('./results', first + '_' + second + '_' + third + '_' + '.json').replace(' ', '')
        with open(save_path, 'w', encoding='utf-8') as js:
            json.dump(self.total_result, js, indent=4, ensure_ascii=False)

        with open(save_path, 'r', encoding='utf-8') as js:
            self.total_result = json.load(js)


        self._parse_result(sql)


def log_init(log_dir):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_name = time.strftime("%Y_%m_%d__%H_%M_%S", time.localtime()) + ".txt"
    logger.add('{}\{}'.format(log_dir, log_name))



if __name__ == '__main__':
    # 日志初始化
    log_init('./log')
    # 初始化
    autogui = AutoGui()

    with open('./SQL.txt', 'r', encoding='utf-8') as f:
        for sql in f.readlines():
            sql = sql.split('\n')[0]

            if autogui.is_processed(sql):
                continue

            logger.info('START: ({})'.format(sql))
            autogui.run(sql)
            logger.info('FINISH: ({})'.format(sql))
