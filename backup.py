# def identify_input_or_output(addr,txs):
# #     # statistic current addr act as an input address in which txs, same to output, and statistic of
# #     # the appearance times of current addr
# #     # addr所在的input tx列表， addr所在的output tx列表， addr在所有tx中出现的次数
# #     input_txs, output_txs, addr_apcount = identify_addr(addr, txs)
# #     # input_txs not empty then output its statistic
# #     print("***************************************************************************************")
# #     if input_txs:
# #         print("This address act as input address for {0} times,".format(len(input_txs)))
# #         statistic_from_txs(input_txs)
# #         return INPUT
# #     else:
# #         print("This address act as output address for {0} times,".format(len(output_txs)))
# #         statistic_from_txs(output_txs)
# #         return OUTPUT