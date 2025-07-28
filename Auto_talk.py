import pyxel
import json

WORDS_SPEED = 3
FONT = pyxel.Font("umplus_j10r.bdf")  # 必要に応じてフォント名を変更

class Auto_Talk:
    def __init__(self, scene, line_number):
        self.scene = scene
        self.line_number = line_number
        self.words_speed = WORDS_SPEED
        self.speaker = ""
        self.message1 = ""
        self.message2 = ""
        self.message3 = ""

        with open("LINE.json", "r", encoding="utf-8") as f:
            self.LINE_data = json.load(f)

    def update_dialogue(self, line_number):
        self.line_number = line_number
        try:
            line_data = self.LINE_data[self.scene][self.line_number]
        except KeyError:
            return
        self.speaker = line_data["speaker"]
        self.message1 = line_data["line"][0]
        self.message2 = line_data["line"][1]
        self.message3 = line_data["line"][2]

    def draw(self, frame_count):
        length1 = min(len(self.message1), frame_count // self.words_speed)
        length2 = min(len(self.message2), (frame_count - len(self.message1) * self.words_speed) // self.words_speed)
        length3 = min(len(self.message3), (frame_count - (len(self.message1) + len(self.message2)) * self.words_speed) // self.words_speed)

        window_y = pyxel.height - 38
        pyxel.rect(10, window_y - 10, pyxel.width - 20, 38, 7)
        pyxel.text(12, window_y - 20, self.speaker, 7, FONT)
        pyxel.text(12, window_y - 8, self.message1[:length1], 0, FONT)

        if length1 == len(self.message1):
            pyxel.text(10, window_y + 4, self.message2[:length2], 0, FONT)
        if length2 == len(self.message2):
            pyxel.text(10, window_y + 16, self.message3[:length3], 0, FONT)

    def is_message_complete(self, frame_count):
        total_chars = len(self.message1) + len(self.message2) + len(self.message3)
        return frame_count >= total_chars * self.words_speed


class App:
    def __init__(self):
        pyxel.init(256, 256)
        self.scene = "nonta_talk1"
        self.line_number = "1"
        self.frame_counter = 0

        self.message = Auto_Talk(self.scene, self.line_number)
        self.message.update_dialogue(self.line_number)

        pyxel.run(self.update, self.draw)

    def update(self):
        self.frame_counter += 1

        if pyxel.btnp(pyxel.KEY_SPACE) and self.message.is_message_complete(self.frame_counter):
            self.line_number = str(int(self.line_number) + 1)
            self.message.update_dialogue(self.line_number)
            self.frame_counter = 0

    def draw(self):
        pyxel.cls(0)
        self.message.draw(self.frame_counter)

App()