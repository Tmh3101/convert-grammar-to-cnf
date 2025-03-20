import copy
from itertools import combinations

def read_grammar_from_file(file_name):
    grammar = {}
    with open(file_name, 'r') as f:
        # Dòng đầu tiên chứa số lượng các luật sinh
        num_rules = int(f.readline())
        # Dòng thứ 2 là chuỗi bắt đầu
        start = f.readline().strip()
        # Các dòng tiếp theo chứa các luật sinh
        for _ in range(num_rules):
            rule = f.readline().strip()
            left, right = rule.split('->')
            left = left.strip()
            grammar[left] = {tuple(p.strip().split()) for p in right.split('|')}

    return grammar, start

def print_grammar(grammar, start=None):
    # In ra chuỗi bắt đầu
    if start is not None:
        print("S =", start)
    # In ra các luật sinh
    for left, right in grammar.items():
        print(left, "->", " | ".join([" ".join(p) for p in right]))

def is_epsilon(c):
    return c[0] == 'epsilon' or c == 'epsilon'

def is_terminal(c):
    return is_epsilon(c) or (97 <= ord(c) <= 122)

def keep_rule(grammar, new_v):
    new_grammar = copy.deepcopy(grammar)
    for left, right in grammar.items():
        if left not in new_v:
            del new_grammar[left]
        else:
            for value in right:
                if all([(is_terminal(c)) or (c in new_v) for c in value]):
                    continue
                new_grammar[left].remove(value)

    return new_grammar

# Loại bỏ các ký hiệu vô ích
def remove_useless_sysbols(grammar, start):
    old_v = set()
    new_v = set()
    for left, right in grammar.items():
        for value in right:
            if all([is_terminal(c) for c in value]):
                new_v.add(left)

    # Bổ đề 1
    while old_v != new_v:
        old_v = copy.deepcopy(new_v)
        for left, right in grammar.items():
            for value in right:
                if all([(is_terminal(c)) or (c in old_v) for c in value]):
                    new_v.add(left)

    grammar = keep_rule(grammar, new_v)

    # Bổ đề 2
    old_v = set()
    new_v = {start}
    while old_v != new_v:
        old_v = copy.deepcopy(new_v)
        for left, right in grammar.items():
            if left in new_v:
                for value in right:
                    for c in value:
                        if not is_terminal(c):
                            new_v.add(c)

    grammar = keep_rule(grammar, new_v)
    return grammar

def generate_rule_with_nullable(value, nullable):
    value_list = list(value)  # Chuyển tuple thành list để dễ xử lý
    result = set()
    for i in range(len(nullable)):
        # combinations(nullable, i + 1) - tạo ra tất cả tập con của nullable có độ dài r + 1 (1 -> len(nullable))
        # combinations tạo tập gồm các giá trị sẽ bị xóa khỏi value
        for combo in combinations(nullable, i + 1):
            temp = value_list.copy()
            # Xóa từng ký tự trong combo khỏi value
            for pattern in combo:
                if pattern in temp:
                    temp.remove(pattern) # Xóa
            result.add(tuple(temp)) # Chuyển lại thành tuple và thêm vào result
            
    result.discard(tuple()) # Xóa tuple rỗng - không phải tất cả đều bị xóa
    return result

# Loại bỏ các luật sinh epsilon
def remove_epsilon_rule(grammar, start):
    # Bước 1: Xác định tập biến rỗng - Nullable
    nullable = set()
    old_nullable = set()
    while True:
        old_nullable = copy.deepcopy(nullable)
        for left, right in grammar.items():
            for value in right:
                if is_epsilon(value) or all([c in nullable for c in value]):
                    nullable.add(left)
                    break
        if old_nullable == nullable:
            break

    # Bước 2: Xây dựng tập luật sinh P' - không chứa epsilon
    new_grammar = copy.deepcopy(grammar)
    for left, right in grammar.items():
        for value in right:
            if is_epsilon(value):
                new_grammar[left].remove(value)
            else:
                new_grammar[left].update(generate_rule_with_nullable(value, nullable)) 

    return new_grammar

# Loại bỏ các luật sinh đơn vị
def remove_unit_rule(grammar, start):
    # Tìm tập detal của từng biến
    deltas = {}
    for left, right in grammar.items():
        deltas[left] = {left}
        for value in right:
            if len(value) == 1 and not is_terminal(value[0]):
                deltas[left].add(value[0])

    # Truy xuất tập detal của từng value trong các delta
    old_deltas = {}
    while deltas != old_deltas:
        old_deltas = copy.deepcopy(deltas)
        for d, value in copy.deepcopy(deltas).items():
            for c in value:
                if c != d:
                    deltas[d].update(deltas[c])

    # Thêm các luật sinh dựa vào delta và value
    for d, value in deltas.items():
        # Thêm các luật sinh
        for c in value:
            if c != d:
                grammar[d].update(grammar[c])
        # Xóa các luật sinh sinh ra các giá trị của detal
        for c in value:
            if c != d:
                grammar[d].discard((c,))
    
    return grammar

def create_new_symbol(c):
    return 'C' + str(c)

# Chuyển đổi văn phạm sang dạng chuẩn Chomsky (CNF - Chomsky Normal Form)
def convert_to_cnf(grammar, start):
    # Bước 1: Loại bỏ các ký hiệu vô ích
    grammar = remove_useless_sysbols(grammar, start)
    print('-----Remove useless symbols-----')
    print_grammar(grammar, start)

    # Bước 2: Loại bỏ các luật sinh epsilon
    grammar = remove_epsilon_rule(grammar, start)
    print('-----Remove epsilon rule-----')
    print_grammar(grammar, start)

    # Bước 3: Loại bỏ các luật sinh đơn vị
    grammar = remove_unit_rule(grammar, start)
    print('-----Remove unit rule-----')
    print_grammar(grammar, start)

    # Bước 4: Chuyển đổi các luật sinh có nhiều hơn 2 biến thành các luật sinh có 2 biến
    new_grammar = {}
    nums_new_symbol = 0
    for left, right in grammar.items():
        for value in right:
            new_value = value
            # Nếu chuỗi có 2 ký tự
            if len(value) == 2:
                # Nếu đầu tiên là terminal thì tạo biến mới
                if is_terminal(value[0]):
                    new_symbol = create_new_symbol(value[0])
                    new_grammar[new_symbol] = {(value[0],)}
                    new_value = (new_symbol, value[1])
                # Nếu cuối cùng là terminal thì tạo biến mới
                if is_terminal(value[1]):
                    new_symbol = create_new_symbol(value[1])
                    new_grammar[new_symbol] = {(value[1],)}
                    new_value = (new_value[0], new_symbol)

            if len(value) > 2:
                while len(new_value) > 2:
                    nums_new_symbol += 1
                    new_symbol = create_new_symbol(nums_new_symbol)
                    new_grammar[new_symbol] = {(new_value[0], new_value[1])}
                    new_value = (new_symbol,) + new_value[2:]

            if left not in new_grammar:
                new_grammar[left] = {new_value}
            else:
                new_grammar[left].add(new_value)

    return new_grammar


grammar, start = read_grammar_from_file('input_grammar.txt')
print('-----Input Grammar-----')
print_grammar(grammar, start)

cnf = convert_to_cnf(grammar, start)
print('-----CNF Grammar-----')
print_grammar(cnf)