import telebot
from telebot import types
import random

VOWELS = ["а", "я", "о", "ё", "у", "е", "э", "ю", "ы", "и"]
bot = telebot.TeleBot("")
users_list = dict()
t = open("word_list.txt", encoding='utf-8')
word_list_file = t
word_list = [i for i in word_list_file.readlines()]


def create_question():
    answer = word_list[random.randint(0, len(word_list) - 1)]
    if ' ' not in answer:
        word_lower = answer.lower()
        variants = []
        for i in range(len(word_lower)):
            if word_lower[i] in VOWELS:
                variants.append(word_lower[:i] + word_lower[i].upper() + word_lower[i + 1:])
        if answer in variants:
            variants.remove(answer)
        return [answer, variants]
    else:
        word_lower = answer.lower().split()[0]
        variants = []
        for i in range(len(word_lower)):
            if word_lower[i] in VOWELS:
                variants.append(word_lower[:i] + word_lower[i].upper() + word_lower[i + 1:] + ' ' + ' '.join(
                    answer.lower().split()[1:]))
        if answer in variants:
            variants.remove(answer)
        return [answer, variants]


class Room:
    def __init__(self, message):
        self.chatinfo = message.chat
        self.IsStart = False
        self.last_message_ans = None
        self.last_message_quest = None
        self.correct = 0
        self.total = 0
        self.last_message_reset = None
        self.message_counter = None
        self.game_already = None
        self.there_are_ans = False

    def start_game(self):
        if self.IsStart:
            self.reset()
        else:
            self.IsStart = True
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton(text='Вопрос', callback_data='question')
            markup.add(item1)
            self.message_counter = bot.send_message(self.chatinfo.id, 'Счёт {}/{}'.format(self.correct, self.total))
            self.last_message_quest = self.question()

    def question(self):
        self.there_are_ans = False
        question = create_question()
        self.last_answer = question[0]
        items = []
        cor_answer = types.InlineKeyboardButton(text=question[0], callback_data='Correct_answer')
        markup = types.InlineKeyboardMarkup()
        k = [cor_answer]
        for i in question[1]:
            items.append(types.InlineKeyboardButton(text=i, callback_data='Incorrect_answer'))
        if len(items) <= 2:
            for i in items:
                k.append(i)
        else:
            for i in range(3):
                k.append(items.pop(random.randint(0, len(items) - 1)))
        random.shuffle(k)
        for i in k:
            markup.add(i)
        return bot.send_message(self.chatinfo.id, 'Выберите правильный ответ', reply_markup=markup)

    def answer(self, IsTrue):
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton(text='Следующий вопрос', callback_data='question')
        item2 = types.InlineKeyboardButton(text='Обновить счёт', callback_data='reset')
        markup.add(item1, item2)
        self.there_are_ans = True
        if IsTrue:
            self.correct += 1
            self.total += 1
            bot.edit_message_text('Счёт {}/{}'.format(self.correct, self.total), self.chatinfo.id,
                                  self.message_counter.message_id)
            self.last_message_ans = bot.send_message(self.chatinfo.id, 'Верный ответ', reply_markup=markup)
        else:
            self.total += 1
            bot.edit_message_text('Счёт {}/{}'.format(self.correct, self.total), self.chatinfo.id,
                                  self.message_counter.message_id)
            self.last_message_ans = bot.send_message(self.chatinfo.id,
                                                     'Неверный ответ, правильный - {}'.format(self.last_answer),
                                                     reply_markup=markup)
        self.there_are_ans = True

    def send_question(self):
        bot.delete_message(self.chatinfo.id, self.last_message_quest.message_id)
        bot.delete_message(self.chatinfo.id, self.last_message_ans.message_id)
        self.last_message_quest = self.question()

    def reset(self):
        self.correct = 0
        self.total = 0
        try:
            bot.edit_message_text('Счёт {}/{}'.format(self.correct, self.total), self.chatinfo.id,
                              self.message_counter.message_id)
        except telebot.apihelper.ApiTelegramException:
            pass
        try:
            bot.delete_message(self.chatinfo.id, self.last_message_quest.message_id)
            bot.delete_message(self.chatinfo.id, self.last_message_ans.message_id)
        except telebot.apihelper.ApiTelegramException:
            pass
        except AttributeError:
            pass

        self.last_message_quest = self.question()


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in users_list:
        user = Room(message)
        users_list[message.chat.id] = user
    users_list[message.chat.id].start_game()
    bot.delete_message(users_list[message.chat.id].chatinfo.id, message.id)


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.message.chat.id in users_list.keys():
        if call.data == 'question':
            users_list[call.message.chat.id].send_question()
        if call.data == 'Correct_answer':
            if  users_list[call.message.chat.id].there_are_ans == False:
                users_list[call.message.chat.id].answer(True)
        if call.data == 'Incorrect_answer':
            if users_list[call.message.chat.id].there_are_ans == False:
                users_list[call.message.chat.id].answer(False)
        if call.data == 'reset':
            users_list[call.message.chat.id].reset()


bot.infinity_polling(allowed_updates=False)
