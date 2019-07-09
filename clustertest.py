from dbconn import connectDB
import json
from prettytable import PrettyTable

INPUT = 0
OUTPUT = 1

def println(title,alist):
    # for i in alist:
    #     print(i)
    t = PrettyTable([title])
    for i in alist:
        t.add_row([i])
    print(t)


def wallet_real_cluster(addr):
    db = connectDB.SQL()
    sql = """SELECT * FROM `userwallet` """
    user_wallet_info = db.select(sql)
    db.close()

    # retrieve user wallet information, do gathering
    cluster_list = []
    target_id = -1
    # find the user id corresponding to the given address
    for i in range(len(user_wallet_info)):
        if user_wallet_info[i][2] == addr:
            target_id = user_wallet_info[i][1]
            print("This given address '{0}' belong to user{1}".format(addr, target_id))
    # if given address is in user wallet, found the real cluster for the given address
    if int(target_id) >= 0:
        for i in range(len(user_wallet_info)):
            if user_wallet_info[i][1] == target_id:
                cluster_list.append(user_wallet_info[i][2])
    println("Real Result",cluster_list)
    return cluster_list


def preprocessing():
    # 1.Read from database and data preprocessing
    #   1.1 Transform records to json format, save txs in a list.
    #   1.2 Retrieve all addresses and remove duplicates.
    db = connectDB.SQL()
    sql = """SELECT * FROM `transactions` """
    db_records = db.select(sql)
    db.close()
    address_temp = []
    txs = []
    # db_records example:
    # ((1, '{"input": [], "output": [{"to_addr": "14KpNE1Svm3hgLF47XsPGSMDUdoo2EnL1y", "value": 100000}]}'),)
    for i in range(len(db_records)):
        tx = json.loads(db_records[i][1])
        # tx example:
        # {"input": [], "output": [{"to_addr": "14KpNE1Svm3hgLF47XsPGSMDUdoo2EnL1y", "value": 100000}]}')
        txs.append(tx)
        if not tx['input']:
            pass
        else:
            for j in range(len(tx['input'])):
                address_temp.append(tx['input'][j]['to_addr'])

        for z in range(len(tx['output'])):
            address_temp.append(tx['output'][z]['to_addr'])

    # address contains all addresses ever appeared with duplication removed
    # txs contains all recorded transactions in database
    address = list(set(address_temp))
    # print(address)
    return address, txs

# 2. for each given address, identify all the transaction involved with
    # return with its identification and corresponding related txs;

# Deprecated
def addrs_appear_count(addr,txid,txs):
    addr_appearance_count = 0
    for i in range(txid):
        for j in range(len(txs[i]['input'])):
            if addr == txs[i]['input'][j]['to_addr']:
                addr_appearance_count = addr_appearance_count + 1
        for j in range(len(txs[i]['output'])):
            if addr == txs[i]['output'][j]['to_addr']:
                addr_appearance_count = addr_appearance_count + 1
    return addr_appearance_count

def addrs_appear_count_all(addr,tx_id,txs):
    addrs_appear_count=0
    # remove current transaction appearance of addr
    other_txs=txs.copy()
    other_txs.pop(tx_id)
    for tx in other_txs:
        for j in range(len(tx['input'])):
            if addr == tx['input'][j]['to_addr']:
                addrs_appear_count = addrs_appear_count + 1
                # print("Appeared in transaction[{0}]".format(txs.index(tx)+1))
        for j in range(len(tx['output'])):
            if addr == tx['output'][j]['to_addr']:
                addrs_appear_count = addrs_appear_count + 1
                # print("Appeared in transaction[{0}]".format(txs.index(tx)+1))
    return addrs_appear_count

# Deprecated
def identify_involved_txs(addr,txs):
    input_txs, output_txs = identify_addr(addr, txs)
    # total_txs = input_txs + output_txs
    total_txs = input_txs
    print("The given address '{0}'involved in {1} transactions".format(addr,len(total_txs)))
    return total_txs

# identify input_txs list and output_txs list respectively for the given address
def identify_addr(addr,txs):
    involved_input_txs = []
    involved_output_txs = []
    for tx in txs:
        for j in range(len(tx['input'])):
            if addr == tx['input'][j]['to_addr']:
                tx_temp = []
                # record tx_id and tx details
                tx_temp.append(txs.index(tx))
                tx_temp.append(tx)
                involved_input_txs.append(tx_temp)
        for j in range(len(tx['output'])):
            if addr == tx['output'][j]['to_addr']:
                tx_temp = []
                # record tx_id and tx details
                tx_temp.append(txs.index(tx))
                tx_temp.append(tx)
                involved_output_txs.append(tx_temp)
    print("The given address '{0}'involved in {1} transactions ".format(addr, (
                len(involved_output_txs) + len(involved_input_txs))))
    # rint(type(involved_input_txs[0][0]))
    return involved_input_txs, involved_output_txs

# Determine if two list have overlap element, no-false/yes-true
def is_two_list_overlap(l1,l2):
    list_c = [a for a in l1 if a in l2]
    if len(list_c) == 0:
        return False
    else:
        return True

# Deprecated
def clustering_from_three_types(inputNum, outputNum, inputAddrs, outputAddrs,tx_id,txs):

    cluster_list=[]
    flagOTC, change_addr = is_one_time_chance(inputNum, outputNum, inputAddrs, outputAddrs,tx_id,txs)
    flagCS = is_comman_spending(inputNum,outputNum)
    flagCB = is_coinbase(inputNum,outputNum)
    # OTC--all input addresses and the change address belong to same entity
    if flagOTC:
        cluster_list.extend(inputAddrs)
        cluster_list.append(change_addr)
    # CS--all input addresses belong to same entity
    if flagCS:
        cluster_list.extend(inputAddrs)
    # CB--all output addresses belong to same entity
    if flagCB:
        pass
    # print(cluster_list)
    return cluster_list

# Determine if it's an OTC tx type
def is_one_time_chance(inputNum, outputNum, inputAddrs, outputAddrs,tx_id,txs):
    changeAddr = ""
    # if outputNum == 2 and inputNum != 2:
    # but in our project, we do not involve mixer transaction, so this filter can be ignored
    if outputNum == 2:
        print("One-time-change transaction")
        # if two list do not have same element, then find out the change address
        if not is_two_list_overlap(inputAddrs,outputAddrs):
            addr1=outputAddrs[0]
            addr2=outputAddrs[1]
            addr1_count = addrs_appear_count_all(addr1, tx_id, txs)
            print("output address1 '{0}' appeared {1} times in transactions".format(addr1, addr1_count))
            addr2_count = addrs_appear_count_all(addr2, tx_id, txs)
            print("output address2 '{0}' appeared {1} times in transactions".format(addr2, addr2_count))

            if addr1_count >= 2 and addr2_count < 2:
                changeAddr = addr2
                print("address '{0}' is more likely a change address".format(changeAddr))
                return True, changeAddr
            elif addr2_count >= 2 and addr1_count < 2:
                changeAddr = addr1
                print("address '{0}' is more likely a change address".format(changeAddr))
                return True, changeAddr
            else:
                print("Cannot tell which address is a change address!")
                return False, None

        else:
            return False, None
    else:
        return False, None

# Determine if it's an CS tx type
def is_comman_spending(inputNum,outputNum):
    if outputNum == 1 and inputNum > 0:
        print("Common spending transaction")
        return True
    else:
        return False

# Determine if it's an CB tx type
def is_coinbase(inputNum,outputNum):
    if outputNum == 1 and inputNum == 0:
        print("Coinbase transaction")
        return True
    else:
        return False

# Parse out input and output addresses number, input addrs and output addrs list, tx_id of the involved tx
def statistic_from_tx(tx_record):
    input_addrs = []
    output_addrs = []
    input_num = len(tx_record[1]['input'])
    output_num = len(tx_record[1]['output'])
    tx_id = tx_record[0]

    print("Transaction {0} has {1} input and {2} output".format(tx_record[0]+1, input_num, output_num))

    for i in range(input_num):
        input_addrs.append(tx_record[1]['input'][i]['to_addr'])
    for j in range(output_num):
        output_addrs.append(tx_record[1]['output'][j]['to_addr'])

    return input_num, output_num, input_addrs, output_addrs, tx_id

# Get a cluster for currenr addr and involved txs_record for input and output respectivly
def analyze_involved_txs(addr,txs_record,txs,flag):
    addr_cluster = []
    addr_cluster.append(addr)
    if flag == INPUT:
        for tx_record in txs_record:
            print("************************************************************")
            print("This addr act as an input address!")
            inputNum, outputNum, inputAddrs, outputAddrs, tx_id = statistic_from_tx(tx_record)
            cluster_list=clustering_from_input_addrs(inputNum, outputNum, inputAddrs, outputAddrs, tx_id,txs)
            addr_cluster.extend(cluster_list)

        addr_cluster = remove_duplicate_elements_from_list(addr_cluster)
    elif flag == OUTPUT:
        for tx_record in txs_record:
            print("************************************************************")
            print("This addr act as an output address!")
            inputNum, outputNum, inputAddrs, outputAddrs, tx_id = statistic_from_tx(tx_record)
            cluster_list=clustering_from_output_addrs(addr,inputNum, outputNum, inputAddrs, outputAddrs, tx_id,txs)
            addr_cluster.extend(cluster_list)

        addr_cluster = remove_duplicate_elements_from_list(addr_cluster)
    return addr_cluster


def clustering_from_input_addrs(inputNum, outputNum, inputAddrs, outputAddrs, tx_id, txs):
    cluster_list = []
    flagOTC, change_addr = is_one_time_chance(inputNum, outputNum, inputAddrs, outputAddrs, tx_id, txs)
    flagCS = is_comman_spending(inputNum, outputNum)

    # OTC--all input addresses and the change address belong to same entity
    if flagOTC:
        cluster_list.extend(inputAddrs)
        cluster_list.append(change_addr)
    # CS--all input addresses belong to same entity
    if flagCS:
        cluster_list.extend(inputAddrs)
    # CB--all output addresses belong to same entity

    # print(cluster_list)
    return cluster_list


def clustering_from_output_addrs(addr, inputNum, outputNum, inputAddrs, outputAddrs, tx_id, txs):
    cluster_list = []
    flagOTC, change_addr = is_one_time_chance(inputNum, outputNum, inputAddrs, outputAddrs, tx_id, txs)
    flagCB = is_coinbase(inputNum, outputNum)
    # OTC--all input addresses and the change address belong to same entity
    if flagOTC and change_addr == addr:
        cluster_list.extend(inputAddrs)
        cluster_list.append(change_addr)
    if flagCB:
        pass
    return cluster_list


def get_a_cluster_from_an_address(addr, txs):
    # Firstly, find all involved input and output txs respectivly
    input_txs, output_txs = identify_addr(addr, txs)
    # for input txs: do clustering
    cl1 = analyze_involved_txs(addr, input_txs, txs, INPUT)
    # for output txs: do clustering
    cl2 = analyze_involved_txs(addr, output_txs, txs, OUTPUT)
    # Merge two list and remove duplicates
    cl=remove_duplicate_elements_from_list(cl1+cl2)
    print("result:{0}".format(cl))
    return cl

def remove_duplicate_elements_from_list(dlist):
    result = list(set(dlist))

    return result

def remove_duplicates(new,old):
    list_new = [x for x in new if x not in old]
    return list_new

def re_cluster(old_cluster,new_cluster,txs):
    tmp_cluster = old_cluster.copy()
    for ad in new_cluster:
        tmp_cluster.extend(get_a_cluster_from_an_address(ad, txs))
    tmp_cluster = remove_duplicate_elements_from_list(tmp_cluster)
    new_cluster = remove_duplicates(tmp_cluster,old_cluster)
    if len(new_cluster) == 0:
        return tmp_cluster
    return re_cluster(tmp_cluster,new_cluster,txs)

def recur_cluster(addr,txs):
    # addr = "1BvLef6YqEaA35L7C9xq7j8W3GJ2GFbDik"

    # initialize old_cluster only has the given address
    old_cluster = []
    old_cluster.append(addr)
    final_cluster = []
    new_cluster = get_a_cluster_from_an_address(addr,txs)

    while len(old_cluster) != len(new_cluster):

        final_cluster_temp = []
        temp_cluster = remove_duplicates(new_cluster,old_cluster)
        for ad in temp_cluster:
            temp = get_a_cluster_from_an_address(ad, txs)
            final_cluster_temp = new_cluster + temp
        final_cluster=list(set(final_cluster_temp))
        old_cluster = new_cluster.copy()
        new_cluster = final_cluster

    println("Clustering Result",final_cluster)



def statistic_from_raw_txs(txs):
    cs_list=[]
    for tx in txs:
        input_num=len(tx['input'])
        output_num=len(tx['output'])
        if is_comman_spending(input_num,output_num):
            print("{0}|{1}".format(txs.index(tx)+1, tx))
            cs_list.append(tx)
    print("Total num of commen spending tx is {0}".format(len(cs_list)))
    return len(cs_list)

def main():

    # method 1
    addrs, txs = preprocessing()

    addr = "12qnFUMWGUiGCNy3dhw57NHQyPyW78gmg8"
    recur_cluster(addr, txs)
    wallet_real_cluster(addr)

    # # method 2
    # addrs, txs = preprocessing()
    # addr = "1NdufxUjo63f9dQ2ov9bCpNsXd23wbgaD6"
    # recur_cluster(addr, txs)
    # wallet_real_cluster(addr)

if __name__ == "__main__":
    # test()
    main()

    # wallet_real_cluster()

