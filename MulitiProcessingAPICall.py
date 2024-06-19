# import time
# from multiprocessing import Process, Pipe
# import requests
# import os
# import StringUtil
# import Constants
# import angaza_util


# def get_customer_details_by_level(level, account_angaza_id):
#     if StringUtil.is_null_or_empty(account_angaza_id):
#         account_angaza_id = ""
#     params = {'account_qid': account_angaza_id}

#     # username = 'joseph+ke@greenlightplanet.com'
#     # password = 'ongany4me2'

#     # production
#     username = os.environ['AUTH_USERNAME']
#     password = os.environ['AUTH_PASSWORD']

#     if level == "account":
#         print('fetching account')
#         r = requests.get(url='https://admin.glpapps.com/glpadmin/angaza/account/by_account_angaza_id/KENYA/{}'.format(account_angaza_id))
#         ac_data = {"data": r.json(), "status_code": r.status_code}
#         print('account fetched')
#         return ac_data

#     if level == "activation":
#         print('fetching activation')
#         r = requests.get(url='https://admin.glpapps.com/glpadmin/angaza/activations/KENYA', params=params)
#         a_data = {"data": r.json(), "status_code": r.status_code}
#         print('activation fetched')
#         return a_data

#     if level == "payment":
#         print('fetching payment')
#         r = requests.get(url='https://admin.glpapps.com/glpadmin/angaza/payments/by_account_id/KENYA/{}?is_exact_same_response=1'.format(account_angaza_id))
#         p_data = {"data": r.json(), "status_code": r.status_code}
#         print('payment fetched')
#         return p_data


# class Parallel(object):

#     def call_funtion_and_send_result(self, level, account_angaza_id, conn):
#         """
#         call the apis by level
#         """
#         temp = get_customer_details_by_level(level, account_angaza_id)
#         res = {
#             level: temp
#         }
#         # print(res)
#         print(level + ' returned')
#         conn.send(res)
#         conn.close()
#         print(level + ' closed')

#     def call_funtion_and_send_result_2(self, api_data, api, country, conn, area):
#         temp = {}
#         # if StringUtil.equals_ignore_case(Constants.ANGAZA_ACCOUNTS_GET, api):
#         #     try:
#         #         temp = angaza_util.get_account_from_angaza_by_account_angaza_id(account_angaza_id=api_data, country=country)
#         #     except Exception as e:
#         #         print("Exception occured while multiprocessing. Exception Details: {}".format(repr(e)))
#         #         temp['error'] = repr(e)
#         if StringUtil.equals_ignore_case(Constants.ANGAZA_ACCOUNTS_DETAILS_BY_CLIENT_IDS_GET, api):
#             try:
#                 temp = angaza_util.get_accounts_details_by_client_id(client_id=api_data, country=country, area=area)
#             except Exception as e:
#                 print("Exception occured while multiprocessing. Exception Details: {}".format(repr(e)))
#                 temp['error'] = repr(e)

#         res = {
#             api_data: temp
#         }
#         # print(res)
#         print("{} returned".format(api_data))
#         conn.send(res)
#         conn.close()
#         print("{} closed".format(api_data))

#     def get_combined_result_2(self, api, api_data_list, country, area):

#         # create a list to keep all processes
#         processes = []

#         # create a list to keep connections
#         parent_connections = []

#         # create a process per api_data

#         for api_data in api_data_list:
#             print("creating process for {}".format(api_data))
#             parent_conn, child_conn = Pipe()
#             parent_connections.append(parent_conn)

#             # create the process, pass instance and connection
#             process = Process(target=self.call_funtion_and_send_result_2, args=(api_data, api, country, child_conn, area,), name=api_data)
#             processes.append(process)

#         # start all processes
#         for process in processes:
#             print('starting process for ' + str(process.name))
#             process.start()

#         data = {}
#         for parent_connection in parent_connections:
#             res = parent_connection.recv()
#             # print(res)
#             for api_data in api_data_list:
#                 if api_data in res:
#                     data[api_data] = res.get(api_data)

#         # make sure that all processes have finished
#         for process in processes:
#             print('joining process for ' + str(process.name))
#             process.join()

#         return data

#     def get_combined_result(self, levels, account_angaza_id):

#         # create a list to keep all processes
#         processes = []

#         # create a list to keep connections
#         parent_connections = []

#         # create a process per level

#         for level in levels:
#             print('creating process for ' + level)
#             parent_conn, child_conn = Pipe()
#             parent_connections.append(parent_conn)

#             # create the process, pass instance and connection
#             process = Process(target=self.call_funtion_and_send_result, args=(level, account_angaza_id, child_conn,), name=level)
#             processes.append(process)

#         # start all processes
#         for process in processes:
#             print('starting process for ' + process.name)
#             process.start()

#         data = {}
#         for parent_connection in parent_connections:
#             res = parent_connection.recv()
#             # print(res)
#             for lvl in levels:
#                 if lvl in res:
#                     data[lvl] = res.get(lvl)

#         # make sure that all processes have finished
#         for process in processes:
#             print('joining process for ' + process.name)
#             process.join()

#         return data


# def call_parallel_api_processing(levels, account_angaza_id):
#     _start = time.time()
#     parallels = Parallel()
#     total_result = parallels.get_combined_result(levels, account_angaza_id)
#     print(total_result)
#     print("Parallel execution time: %s seconds" % (time.time() - _start))
#     return total_result


# def call_same_api_with_different_data(api, api_data_list, country, area=None):
#     print('Enter call_parallel_reject_cases_processing')
#     _start = time.time()
#     parallels = Parallel()
#     total_result = parallels.get_combined_result_2(api, api_data_list, country, area)
#     print(total_result)
#     print("Parallel execution time: %s seconds" % (time.time() - _start))
#     print('Exit call_parallel_reject_cases_processing')
#     return total_result
