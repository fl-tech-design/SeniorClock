import json
import time
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen

# from plyer import vibrator

Config.set('graphics', 'width', '390')
Config.set('graphics', 'height', '800')


def r_json():
    with open("data.json", "r", encoding='UTF-8') as file:
        data_dict = json.load(file)
    return data_dict


def set_act_data(act_key, act_data):
    """ WRITE THE NEW HIGH-SCORE TO THE .JSON FILE """
    data = r_json()
    data["app"][act_key] = act_data
    with open("data.json", "w", encoding='UTF-8') as file:
        json.dump(data, file)


def set_timer(act_key, act_data):
    """ WRITE THE NEW HIGH-SCORE TO THE .JSON FILE """
    data = r_json()
    data["app"]["act_timer"][act_key] = act_data
    with open("data.json", "w", encoding='UTF-8') as file:
        json.dump(data, file)


def play_audio(audio_name):
    """play the audiofile. file format .wav"""
    sound = SoundLoader.load(audio_name)
    sound.volume = 0.6
    sound.play()


class ClockView(FloatLayout):
    def __init__(self):
        super(ClockView, self).__init__()
        self.now = None
        self.data = r_json()
        self.act_language = self.data["app"]["act_lang"]
        self.counter = 0

    def update(self, *args):
        print(args)
        self.data = r_json()
        self.act_language = self.data["app"]["act_lang"]
        self.now = datetime.now()
        self.set_label_day_str()
        self.set_label_clock()
        self.set_label_date()
        self.ids.b_set.text = self.data[self.act_language]["label"]["l_setting"]
        self.ids.b_tim.text = self.data[self.act_language]["label"]["l_timer"]
        self.counter += 1

    def set_label_day_str(self):
        day_name = self.now.strftime("%a")
        dict_day = self.data[self.act_language]["day"]
        act_day_str = dict_day[day_name]
        len_act_day_str = len(act_day_str)
        if len_act_day_str > 7:
            self.ids.day_str.font_size = dp(70)
        else:
            self.ids.day_str.font_size = dp(90)
        self.ids.day_str.text = act_day_str

    def set_label_date(self):
        act_day = self.now.strftime("%d")
        if int(act_day) < 10:
            act_day = act_day.replace("0", "")
        act_month = self.now.strftime("%b")
        act_year = self.now.strftime("%Y")
        dict_month = self.data[self.act_language]["month"]
        act_month_str = dict_month[act_month]
        if len(act_month_str) > 8:
            self.ids.l_date.font_size = dp(55)
        else:
            self.ids.l_date.font_size: dp(60)

        self.ids.l_date.text = act_day + " " + act_month_str
        self.ids.year.text = act_year

    def set_label_clock(self):
        now = datetime.now()
        hour = now.strftime("%H")
        minute = now.strftime("%M")
        format_time = hour + " " + minute
        clock_color = self.data["app"]["act_c_col"]
        self.ids.points.color = (clock_color["c_red"], clock_color["c_green"], clock_color["c_blue"])
        self.ids.l_clock.text = format_time
        self.ids.l_clock.color = (clock_color["c_red"], clock_color["c_green"], clock_color["c_blue"])

    def set_app_col(self):
        app_color = self.data["app"]["act_a_col"]
        self.ids.day_str.color = (app_color["a_red"], app_color["a_green"], app_color["a_blue"])
        self.day_int.color = (app_color["a_red"], app_color["a_green"], app_color["a_blue"])
        self.l_set.color = (app_color["a_red"], app_color["a_green"], app_color["a_blue"])
        self.year.color = (app_color["a_red"], app_color["a_green"], app_color["a_blue"])

    @staticmethod
    def change_view(view):
        """change to window level one"""
        app.screen_manager.transition.direction = "left"
        app.screen_manager.current = view


class TimerView(FloatLayout):
    def __init__(self):
        super(TimerView, self).__init__()
        self.act_t_h, self.act_t_m, self.act_t_s = (None,) * 3
        self.act_t_dict = {}

        self.a_data = r_json()
        self.a_lang = self.a_data["app"]["act_lang"]
        self.a_font = self.a_data["app"]["act_lang"]
        self.t_stat = self.a_data["app"]["t_stat"]
        self.a_stat = self.a_data["app"]["a_stat"]
        self.ids.b_sta.text = self.a_data[self.a_lang]["label"]["l_start"]

        self.counter = 0

    def update(self, *args):
        print(args)
        self.a_data = r_json()
        self.a_lang = self.a_data["app"]["act_lang"]
        self.act_t_dict = self.a_data["app"]["act_timer"]
        self.act_t_h = self.act_t_dict["t_h"]
        self.act_t_m = self.act_t_dict["t_m"]
        self.act_t_s = self.act_t_dict["t_s"]
        self.t_stat = self.a_data["app"]["t_stat"]
        self.a_stat = self.a_data["app"]["a_stat"]
        if self.counter % 10 == 0:
            self.running_time()
        self.counter += 2
        self.set_labels()
        if self.t_stat <= 1 and self.check_zero():
            self.ids.b_sta.disabled = True
        else:
            self.ids.b_sta.disabled = False
        if self.t_stat == 2:
            self.ids.b_sta.text = self.a_data[self.a_lang]["label"]["l_stop"]
        if self.t_stat == 3 and self.a_stat == 1:
            self.ids.b_sta.text = self.a_data[self.a_lang]["label"]["l_end"]
            play_audio("backend/alarm-clock-short.wav")
            time.sleep(1)

    def set_labels(self):
        if len(self.a_data[self.a_lang]["label"]["l_timer"]) > 7:
            self.ids.l_tit.font_size = dp(60)
        else:
            self.ids.l_tit.font_size = dp(80)
        self.ids.l_tit.text = self.a_data[self.a_lang]["label"]["l_timer"]
        self.ids.b_clo.text = self.a_data[self.a_lang]["label"]["l_clock"]
        self.ids.b_set.text = self.a_data[self.a_lang]["label"]["l_setting"]
        if self.act_t_h < 10:
            self.ids.l_h.text = "0" + str(self.act_t_h)
        else:
            self.ids.l_h.text = str(self.act_t_h)
        if self.act_t_m < 10:
            self.ids.l_m.text = "0" + str(self.act_t_m)
        else:
            self.ids.l_m.text = str(self.act_t_m)
        if self.act_t_s < 10:
            self.ids.l_s.text = "0" + str(self.act_t_s)
        else:
            self.ids.l_s.text = str(self.act_t_s)

    def running_time(self):
        if self.t_stat == 2:
            set_timer("t_s", self.act_t_s - 1)
            if self.act_t_s == 0 and self.act_t_h > 0:
                set_timer("t_h", self.act_t_h - 1)
                set_timer("t_m", 59)
                set_timer("t_s", 59)
            if self.act_t_s == 0 and self.act_t_m > 0:
                set_timer("t_m", self.act_t_m - 1)
                set_timer("t_s", 59)
            if self.act_t_s < 0:
                set_timer("t_s", 0)
            if self.check_zero():
                set_timer("t_s", 0)
                set_act_data("t_stat", 3)
                set_act_data("a_stat", 1)
            print("eof r_time t_stat2____")

    def check_zero(self):
        if self.act_t_h == 0 and self.act_t_m == 0 and self.act_t_s == 0:
            return True
        else:
            return False

    def start_stop(self):
        if self.t_stat == 1:
            set_act_data("t_stat", 2)
            self.ids.b_sta.text = self.a_data[self.a_lang]["label"]["l_start"]
        if self.t_stat == 2:
            self.ids.b_sta.text = self.a_data[self.a_lang]["label"]["l_start"]
            set_act_data("t_stat", 1)
        if self.t_stat == 3 and self.a_stat == 1:
            self.ids.b_sta.text = self.a_data[self.a_lang]["label"]["l_start"]
            set_act_data("t_stat", 0)
            set_act_data("a_stat", 0)

    def sec_up(self):
        if self.act_t_s > 58:
            set_timer("t_s", 0)
        else:
            set_act_data("t_stat", 1)
            set_timer("t_s", self.act_t_s + 1)

    def sec_down(self):
        if self.act_t_s > 0:
            set_timer("t_s", self.act_t_s - 1)

    def min_up(self):
        if self.act_t_m > 58:
            set_timer("t_m", 0)
        else:
            set_act_data("t_stat", 1)
            set_timer("t_m", self.act_t_m + 1)

    def min_down(self):
        if self.act_t_m > 0:
            set_timer("t_m", self.act_t_m - 1)

    def h_up(self):
        if self.act_t_h > 23:
            set_timer("t_h", 0)
        else:
            set_act_data("t_stat", 1)
            set_timer("t_h", self.act_t_h + 1)

    def h_down(self):
        if self.act_t_h > 0:
            set_timer("t_h", self.act_t_h - 1)

    @staticmethod
    def change_view(view):
        """change to window level one"""
        app.screen_manager.transition.direction = "left"
        # vibrator.vibrate(0.1)
        app.screen_manager.current = view


class SettingView(FloatLayout):
    def __init__(self):
        super(SettingView, self).__init__()
        self.a_data = r_json()
        self.set_labels()

    def set_app_data(self, key, font):
        set_act_data(key, font)
        self.set_labels()

    def set_labels(self, *args):
        print(args)
        app_data = r_json()
        act_language = app_data["app"]["act_lang"]
        self.ids.l_titel.text = app_data[act_language]["label"]["l_setting"]
        self.ids.l_lang.text = app_data[act_language]["label"]["l_lang"]
        self.ids.b_clo.text = app_data[act_language]["label"]["l_clock"]
        self.ids.l_b_ger.text = app_data[act_language]["label"]["l_ger"]
        self.ids.l_b_eng.text = app_data[act_language]["label"]["l_eng"]
        self.ids.l_b_fra.text = app_data[act_language]["label"]["l_fra"]
        self.ids.l_b_gre.text = app_data[act_language]["label"]["l_gre"]
        self.ids.l_b_ita.text = app_data[act_language]["label"]["l_ita"]

    @staticmethod
    def change_view(view):
        """change to window level one"""
        app.screen_manager.transition.direction = "right"
        app.screen_manager.current = view


class TimeApp(App):
    def __init__(self):
        super().__init__()
        self.screen_manager, self.clock_view, self.timer_view, self.setting_view = (None,) * 4

    def build(self):
        self.screen_manager = ScreenManager()

        self.clock_view = ClockView()
        screen = Screen(name="clockview")
        screen.add_widget(self.clock_view)
        self.screen_manager.add_widget(screen)
        Clock.schedule_interval(self.clock_view.update, 1)

        self.timer_view = TimerView()
        screen = Screen(name="timerview")
        screen.add_widget(self.timer_view)
        self.screen_manager.add_widget(screen)
        Clock.schedule_interval(self.timer_view.update, 0.2)

        self.setting_view = SettingView()
        screen = Screen(name="settingview")
        screen.add_widget(self.setting_view)
        self.screen_manager.add_widget(screen)
        Clock.schedule_interval(self.setting_view.set_labels, 1)

        return self.screen_manager


if __name__ == "__main__":
    app = TimeApp()
    app.run()
