from dbconn import connectDB
import json

INPUT = 0
OUTPUT = 1

def println(alist):
    for i in alist:
        print(i)


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
    # if given address is in user wallet, found the real cluster for the given address
    if int(target_id) >= 0:
        for i in range(len(user_wallet_info)):
            if user_wallet_info[i][1] == target_id:
                cluster_list.append(user_wallet_info[i][2])
    println(cluster_list)
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
    print(db_records)
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

def addrs_appear_count_all(addr,txs):
    addrs_appear_count=0
    for tx in txs:
        for j in range(len(tx['input'])):
            if addr == tx['input'][j]['to_addr']:
                addrs_appear_count = addrs_appear_count + 1
                print("Appeared in transaction[{0}]".format(tx))
        for j in range(len(tx['output'])):
            if addr == tx['output'][j]['to_addr']:
                addrs_appear_count = addrs_appear_count + 1
                print("Appeared in transaction[{0}]".format(tx))
    return addrs_appear_count


def identify_involved_txs(addr,txs):
    input_txs, output_txs = identify_addr(addr, txs)
    total_txs = input_txs + output_txs
    print("The given address involved in {0} transactions".format(len(total_txs)))
    return total_txs

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

    return involved_input_txs, involved_output_txs

# Determine if two list have overlap element, no-false/yes-true
def is_two_list_overlap(l1,l2):
    list_c = [a for a in l1 if a in l2]
    if len(list_c) == 0:
        return False
    else:
        return True

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
    print(cluster_list)
    return cluster_list

def is_one_time_chance(inputNum, outputNum, inputAddrs, outputAddrs,tx_id,txs):
    tx_id = tx_id - 1
    changeAddr = ""
    if outputNum == 2 and inputNum != 2:
        # if two list do not have same element, then find out the change address
        if not is_two_list_overlap(inputAddrs,outputAddrs):
            addr1=outputAddrs[0]
            addr2=outputAddrs[1]
            # addr1_count = addrs_appear_count(addr1, tx_id, txs)
            addr1_count = addrs_appear_count_all(addr1,txs)
            print("output address {0} appeared {1} times in past transactions".format(addr1, addr1_count))
            # addr2_count = addrs_appear_count(addr2, tx_id, txs)
            addr2_count = addrs_appear_count_all(addr2, txs)
            print("output address {0} appeared {1} times in past transactions".format(addr2, addr2_count))

            if addr1_count > 2 and addr2_count <= 2:
                changeAddr = addr2
                print("address '{0}' is more likely a change address".format(changeAddr))
                return True, changeAddr
            elif addr2_count > 2 and addr1_count <= 2:
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
def is_comman_spending(inputNum,outputNum):
    if outputNum == 1 and inputNum > 0:
        return True
    else:
        return False

def is_coinbase(inputNum,outputNum):
    if outputNum == 1 and inputNum == 0:
        return True
    else:
        return False

def statistic_from_tx(tx_record):
    input_addrs=[]
    output_addrs=[]
    input_num=len(tx_record[1]['input'])
    output_num=len(tx_record[1]['output'])
    # database txid start from 1, here python list start from 0, so...
    tx_id = tx_record[0]+1
    print("Transaction {0} has {1} input and {2} output".format(tx_id,input_num,output_num))

    for i in range(input_num):
        input_addrs.append(tx_record[1]['input'][i]['to_addr'])
    for j in range(output_num):
        output_addrs.append(tx_record[1]['output'][j]['to_addr'])
    # count_list[1]---output count
    # count_list[0]---input count
    return input_num, output_num, input_addrs, output_addrs, tx_id

def analyze_involved_txs(txs_record,txs):
    addr_cluster = []
    for tx_record in txs_record:
        inputNum, outputNum, inputAddrs, outputAddrs, tx_id = statistic_from_tx(tx_record)
        cluster_list=clustering_from_three_types(inputNum, outputNum, inputAddrs, outputAddrs, tx_id,txs)
        addr_cluster.extend(cluster_list)
    return addr_cluster
def main():
    # print("hello world")
    # print("hello world")
    addrs, txs=preprocessing()
    # addr = "1NwFhitnTy59eSsYeHQbkxRySzLHSUm678"
    # total_txs = identify_involved_txs(addr,txs)
    # analyze_involved_txs(total_txs, txs)
    # wallet_real_cluster(addr)

if __name__ == "__main__":
    # test()
    main()
    # wallet_real_cluster()

