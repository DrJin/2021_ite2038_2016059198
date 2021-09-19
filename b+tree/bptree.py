import csv
import sys
import pickle

class Node():
    def __init__(self, keys=[], nodes=[], is_leaf = True, parent=True):
        self.is_leaf = is_leaf #initially leaf
        self.parent = parent  # 부모 노드 존재 유무 -> root 판별용
        self.keys = keys # keys for node(non-leaf and leaf)
        self.nodes = nodes # non-leaf node -> node pointers (항상 len(nodes) = len(leys)+1)
                           # #leaf-node -> value, (but nodes[-1]은 다음 leaf-node)
        # values for leaf-nodes are in BP_tree
    def insert_leaf(self, key, value):
        #print('cur_node', self.keys, self.nodes)

        if len(self.nodes) == 0:
            self.nodes.append(None)  # 맨 뒤에 임시 left-leaf, right-leaf node 추가
        # parent_key = cur_node[0] #부모의 키는 cur_node의 맨 앞키
        next_node = self.nodes.pop()  # 백업
        self.keys.append(key)
        self.nodes.append(value)
        self.keys, self.nodes = map(list, zip(*sorted(zip(self.keys, self.nodes))))  # 정렬
        self.nodes.append(next_node) # 복원



class BP_tree(): #index file

    def __init__(self, degree):
        self.values = [] #values list(linked_list)
        self.degree = degree
        self.root = Node()
        self.root.parent = False
        self.root.is_leaf = True


    def insert(self, cur_node, key, value):
        if not cur_node.is_leaf: #leaf노드가 아니라면
            for i in range(len(cur_node.keys)): 
                if key < cur_node.keys[i]: #key가 작다면
                    left, right = self.insert(cur_node.nodes[i], key, value) #재귀
                    break
            if key >= cur_node.keys[-1]:#만약 모든 key와 비교해 크다면 우측 노드로
                left, right = self.insert(cur_node.nodes[len(cur_node.keys)], key, value)
            
            
            #한바퀴를 돌고서 나온 뒤
            if left != None: #만약 하위 노드에서 분할되어 올라온 노드가 있다면
                
                if right.is_leaf:  # 분할된 노드가 leaf라면
                    insert_key = right.keys[0]  # 우측 노드 첫번째
                else:
                    insert_key = right.keys.pop(0)  # 우측 노드 첫번째 삭제
                
                cur_node.keys.append(insert_key)  # 일단 집어넣기
                cur_node.keys.sort()  # 무조건 정렬하기
                changed_index = cur_node.keys.index(insert_key)  # 바뀐 키의 위치
                
                cur_node.nodes.pop(changed_index)
                cur_node.nodes.insert(changed_index, right)
                cur_node.nodes.insert(changed_index, left)
                

            #하위노드 처리까지 끝내고서
            if len(cur_node.keys) == self.degree:  # 만약 꽉 찼다면
                
                if cur_node.parent:  # 부모노드가 있다면 -> tree 높이는 변함 없음
                    
                    return self.spilt_node(cur_node)  # is_root = False
                else: # 없다면 = root -> root의 분할은 tree 높이가 한단계 올라감 -> non-leaf
                    left, right = self.spilt_node(cur_node)  # is_root = True
                    new_node = Node([], [], False, False)  # root이면서 leaf도 아님
                    insert_key = right.keys.pop(0)  # 우측 노드 첫번째
                    new_node.keys = [insert_key]  # key는 우측 첫번째
                    new_node.nodes = [left, right]
                    self.root = new_node  # root 갱신

        else: #leaf node라면
            cur_node.insert_leaf(key, value) # 키 입력
        
            if len(cur_node.keys) == self.degree: #꽉 찼다면
                
                if cur_node.parent: # 부모노드가 있다면 -> tree 높이는 변함 없음
                    return self.spilt_node(cur_node) #is_root = False
                
                else: #없다면 = root -> root의 분할은 tree 높이가 한단계 올라감
                    
                    left, right= self.spilt_node(cur_node) #is_root = True
                    new_node = Node([], [], False, False)  # root이면서 leaf도 아님
                    insert_key = right.keys[0]  # 우측 노드 첫번째
                    new_node.keys = [insert_key]  # key는 우측 첫번째
                    new_node.nodes = [left, right]
                    self.root = new_node #root 갱신
                    
        return None, None #아무런 변동이 없을 때


    def delete(self, key):
        pass #미구현

    def spilt_node(self, node): #spilt root node
        m = len(node.keys)
        mid = m // 2 - 1 if m % 2 == 0 else m // 2
        if node.is_leaf:  # leaf node라면
            right = Node(node.keys[mid:], node.nodes[mid:])  # 우측 분할
            node.parent = True  # node는 left
            node.keys = node.keys[:mid]
            node.nodes = node.nodes[:mid] + [right]
            node.is_leaf = True
            return node, right #leaf-node root

        else:  # non-leaf라면
            right = Node(node.keys[mid:], node.nodes[mid + 1:], False)  # 우측 분할
            left = Node(node.keys[:mid], node.nodes[:mid + 1], False)  # 좌측 분할
            return left, right #non-leaf node root


    #single_search는 get_path = True
    def find_leaf(self, key, print_path = False):
        cur_node = self.root
        while not cur_node.is_leaf:
            if print_path: #print_path == True라면 경로 출력
                print(",".join([str(key) for key in cur_node.keys]))
            for i in range(len(cur_node.keys)):
                if cur_node.keys[i] > key: #cur_node가 key보다 크다면 (같은 키는 없으므로)
                    cur_node = cur_node.nodes[i] #해당 좌측 하위 노드로
                    break
                elif i == len(cur_node.keys) - 1: #cur_node보다 key가 크거나 같은데 마지막 노드이면
                    cur_node = cur_node.nodes[i+1]#우측 하위 노드로
                    break

        return cur_node

    #key까지 가는 path 출력
    def single_key_search(self, key):
        
        leaf = self.find_leaf(key, print_path=True)

        if key not in leaf.keys:
            print("NOT FOUND!")
            return
        else:
            value = leaf.nodes[leaf.keys.index(key)] #list에서 가져옴
            print(value) #value 출력

    #start부터 end까지 출력
    def ranged_search(self, start, end):
        result = self.find_leaf(start)

        while 1:

            for i in range(len(result.keys)):
                #print(result.keys[i])
                if start <= result.keys[i] <= end: #key가 start와 end 사이에 있다면
                    print(result.keys[i], result.nodes[i], sep=',') #출력
                elif result.keys[i] > end: # 더 커지면
                    break
                
            if result.nodes[-1] == None: #다음 리프노드가 없으면
                break
            
            elif result.keys[-1] <= end:  #마지막 키가 end보다 작거나 같다면
                result = result.nodes[-1] #next leaf node로
                
            else: #마지막 키가 end보다 크다면
                break



#main part

command = sys.argv[1]
index_file = sys.argv[2]
index = None

#get b and index list
def get_index(index_file): #get index
    b = 0
    index = None
    with open(index_file, 'rb') as file:
        try:
            b = pickle.load(file)
            index = pickle.load(file)
        except EOFError:
            pass

    return b, index


def save_index(b, index): #save index
    with open(index_file, 'wb') as file:
        try:
            pickle.dump(b, file)
            pickle.dump(index, file)
        except EOFError:
            pass



#create index
if command == '-c':
    b = int(sys.argv[3])  # size of each node
    with open(index_file, 'wb') as file:
        try:
            pickle.dump(b, file)
            pickle.dump(BP_tree(b), file)  # make new b+tree
        except EOFError:
            pass

#insertion
elif command == '-i':
    data_file = sys.argv[3]
    data = open(data_file)
    data = csv.reader(data)
    data = list(data)
    b, index = get_index(index_file)

    if not index: #if index == None:
        print("Error! Threre are no index!")
        exit(1)

    for line in data:
        key, value = list(map(int,line))
        index.insert(index.root, key, value)

    save_index(b, index)

#deletion --- 미구현
elif command == '-d':
    data_file = sys.argv[3]
    data = open(data_file)
    data = csv.reader(data)
    data = list(data)
    b, index = get_index(index_file)

    if not index:
        print("Error! Threre are no index!")
        exit(1)

    for line in data:
        key, value = list(map(int,line.split()))
        index.delete(key)

    save_index(b, index)

#single key search - print search passes
elif command == '-s':
    key = int(sys.argv[3])
    b, index = get_index(index_file)

    if not index:
        print("Error! Threre are no index!")
        exit(1)

    index.single_key_search(key)


#ragned search - for bptree get start to end
elif command == '-r':
    start_key = int(sys.argv[3])
    end_key = int(sys.argv[4])
    b, index = get_index(index_file)

    if not index:
        print("Error! Threre are no index!")
        exit(1)

    index.ranged_search(start_key, end_key)
    
else:
    print("wrong command!")


