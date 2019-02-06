import random
import string
import pickle

class Order:
    def __init__(self, items, dest, due, start):
        
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.items = items
        self.dest = dest
        self.due = due
        self.start = start


def test_input_dependency_generation(item, prob):
    # 대략적으로 의자 1는 발받침과 함께 쓸 수 있는 의자,
    # 의자 2는 책상과 함께 쓸 수 있는 의자
    # 의자 3는 탁자용 의자라고 하자!

    # 물론 아무 상관 없이 들어올 수도 있다.

    supplementary = []

    if 'table' in item:
        supplementary = ['chair_2'] * random.randrange(1, 5)
    elif 'desk' in item:
        supplementary = ['chair_3']
    elif 'chair_1' in item:
        supplementary = ['footrest']

    if random.random() < prob:

        return [item] + supplementary

    else:
        return [item]


def test_input_generation_randomly(dest, due, start):
    # 탁자 1, 2, 3 의 선호도는 각각 6:3:1
    # 책상 1, 2, 3 의 선호도는 각각 5:4:1

    itemset = []

    tableR = random.random()

    if tableR > 0.4:
        itemset = itemset + test_input_dependency_generation('table_1', 0.7)
    elif tableR > 0.1:
        itemset = itemset + test_input_dependency_generation('table_2', 0.7)
    else:
        itemset = itemset + test_input_dependency_generation('table_3', 0.7)

    deskR = random.random()
    if deskR > 0.5:
        itemset = itemset + test_input_dependency_generation('desk_1', 0.5)
    elif deskR > 0.1:
        itemset = itemset + test_input_dependency_generation('desk_2', 0.5)
    else:
        itemset = itemset + test_input_dependency_generation('desk_3', 0.5)

    chairR = random.random()
    if chairR > 0.65:
        itemset = itemset + test_input_dependency_generation('chair_1', 0.5)

    chairR = random.random()
    if chairR > 0.85:
        itemset = itemset + test_input_dependency_generation('chair_2', 0.5)

    chairR = random.random()
    if chairR > 0.6:
        itemset = itemset + test_input_dependency_generation('chair_3', 0.5)

    return Order(itemset, dest, due, start)

def gen_test_order(name):

    orders = []
    random.seed(11)  # for reproductivity

    dest_cand = ['DOOR_(1,0)', 'DOOR_(4,0)', 'DOOR_(7,0)',
                 'DOOR_(10,0)', 'DOOR_(13,0)', 'DOOR_(16,0)', 'DOOR_(19,0)',
                 'DOOR_(22,0)', 'DOOR_(25,0)', 'DOOR_(28,0)']

    for i in range(50):
        dest = random.choices(dest_cand, k=1)[0]

        start = 25*(i+1) + random.randrange(-6, 6)
        due = start + random.randrange(120, 150)

        generated_order = test_input_generation_randomly(dest, due, start)

        due_adjusted = due + len(generated_order.items) * 14
        generated_order.due = due_adjusted

        orders.append(generated_order)

    with open('./'+name, 'wb') as f:
        pickle.dump(orders, f)

    for o in orders:
        print('\t', o.id, o.items, o.dest)