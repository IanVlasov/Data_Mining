# Data_Mining

В файле runner.py на вход подаются два айдишника юзеров вк.
Алгоритм использует т.н. Breadth-first search вместо стандартного Depth-first search.

На первом шаге идет проверка, не состоят ли переданные айдишники в друзьях,
на втором: нет ли у переданных айдишников общих друзей,
на третьем и последующих:   - идет запрос списка друзей юзера_1.
                            - Список сплитится на списки по 100 юзеров (ограничение апи вк)
                            - проверяется нет ли общих друзей у юзера_2 с переданным списком из 100 айдишников

На выходе в монго записывается первая найденная цепочка друзей.

Интуитивно, мне показался этот способ быстрее, чем прямой перебор друзей, хочу потестить так ли это, но до сдачи уже не успею

Не успел написать приятный аутпут процессор, поэтому расшифрую результат на конкретном примере одного айтема:

{'_id': ObjectId('5dacd5ec6967cc57cb1daafa'),
 'friends_chain': [19587588,                                <- юзер_1 (передан на входе)
                   81771,                                   <- друг_1 в цепочке
                   [{'common_count': 1,
                     'common_friends': [178913514],         <- список общих друзей друга_2 и юзера_2
                     'id': 11081576},                       <- друг_2 в цепочке
                    {'common_count': 1,
                     'common_friends': [152465],            <- список общих друзей другого_друга_2 и юзера_2
                     'id': 11264606}],                      <- другой_друг_2 в цепочке
                   20367747]}                               <- юзер_2 (передан на входе)

Фактически, выше представлены 2 цепочки, отличающиеся 3 и 4 айдишниками:
[19587588, 81771, 11081576, 178913514, 20367747]
и
[19587588, 81771, 11264606, 152465, 20367747]