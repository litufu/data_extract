# _author : litufu
# date : 2018/4/14
import difflib
import Levenshtein

def similar(seq1, seq2):
    if len(seq1)>len(seq2):
        return Levenshtein.ratio(seq1[:len(seq2)], seq2) > 0.55
    else:
        return Levenshtein.ratio(seq1, seq2[:len(seq1)]) > 0.55
    #是否seq2被截断了，导致seq1和seq2不一致，因此对seq1进行截断操作

def similar_list(list1,list2):
    '''寻找两个列表中所有的相似元素
    list1中有多少个元素和list2中的相似
    '''
    similar_lst = []
    for item1 in list1:
        for item2 in list2:
            if similar(item1,item2):
                similar_lst.append(item1)
                break
    return similar_lst

def similar_item_with_list(item,list):
    '''
    判断某个元素是否与列表中的某个元素相似
    :param item:
    :param list:
    :return:
    '''
    for i in list:
        if similar(item,i):
            list.remove(i)
            return i
    return None

if __name__ == '__main__':
    for i in range(10):
        for j in range(11):
            print('i',i)
            print('j',j)
            if j > i:
                break
