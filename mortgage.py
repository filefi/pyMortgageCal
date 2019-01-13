#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-1-13 20:52
# @Author  : filefi
# @Site    : 
# @File    : mortgage.py
# @Software: PyCharm


import numpy as np
import pylab as pl
from datetime import datetime
from decimal import Decimal


class Mortgage:
    """

    """

    def __init__(self, total_principal: int, period: int, base_interest_rate: Decimal, first_payment: datetime,
                 equal_installments=True):
        """

        :param total_principal: 全部本金（万）
        :param period: 贷款年限
        :param first_payment: 首次还款日期,datetime对象实例
        :param base_interest_rate: 基准利率
        :param equal_installments: 贷款等额本息，默认只能计算等额本息
        """
        self.total_principal = total_principal * 10000
        self.month_amount = period * 12
        self.first_payment = first_payment
        self.base_interest_rate = base_interest_rate / (12 * 100)  # convert 4.9 to 0.049
        self.equal_installments = equal_installments
        # 每月月供额
        self.monthly_repayment = None
        # 月供总额
        self.repayment_amount = None
        # 利息总额
        self.interest_amount = None
        # 每年还款情况，年月供对象的列表
        self.yearly_repayment_list = []

    def calculate_equal_installments(self):
        # 每月月供
        self.monthly_repayment = (self.total_principal * self.base_interest_rate * (
                1 + self.base_interest_rate) ** self.month_amount) / (
                                         (1 + self.base_interest_rate) ** self.month_amount - 1)

        # 月供总额
        self.repayment_amount = self.monthly_repayment * self.month_amount

        # 利息总额
        self.interest_amount = self.monthly_repayment * self.month_amount - self.total_principal

        # 当前月份
        current_month = self.first_payment.month
        # 当前年份
        current_year = self.first_payment.year
        # 当月还款后剩余还款总额
        curr_month_remain_repayment_amount = self.repayment_amount
        # 当月还款后剩余本金
        curr_month_remain_principal_amount = self.total_principal
        # 当月还款后剩余利息
        curr_month_remain_interest_amount = self.interest_amount
        # 当前已还月供总额
        repaid_repayment_amount = 0
        # 当前已还本金总额
        repaid_principal_amount = 0
        # 当前已还利息总额
        repaid_interest_amount = 0
        monthly_repayment_list = []

        for i in range(1, self.month_amount + 1):
            # 当月应还利息
            current_month_interest = self.total_principal * self.base_interest_rate * (
                    (1 + self.base_interest_rate) ** self.month_amount - (1 + self.base_interest_rate) ** (i - 1)) / (
                                             (1 + self.base_interest_rate) ** self.month_amount - 1)
            # 当月应还本金
            current_month_principal = self.total_principal * self.base_interest_rate * (
                    1 + self.base_interest_rate) ** (i - 1) / (
                                              (1 + self.base_interest_rate) ** self.month_amount - 1)
            # 当月利息占比
            current_interest_percentage = current_month_interest * 100 / self.monthly_repayment

            # 当月还款后剩余还款总额
            curr_month_remain_repayment_amount -= self.monthly_repayment
            # 当月还款后剩余本金
            curr_month_remain_principal_amount -= current_month_principal
            # 当月还款后剩余利息
            curr_month_remain_interest_amount -= current_month_interest

            # 当前已还月供总额
            repaid_repayment_amount += self.monthly_repayment
            # 当前已还本金总额
            repaid_principal_amount += current_month_principal
            # 当前已还利息总额
            repaid_interest_amount += current_month_interest

            # 每月月供对象实例
            monthly_repayment = MonthlyRepayment(months=i, month=current_month, repayment=self.monthly_repayment,
                                                 principal=current_month_principal,
                                                 interest=current_month_interest,
                                                 interest_percentage=current_interest_percentage,
                                                 remain_repayment_amount=curr_month_remain_repayment_amount,
                                                 remain_principal_amount=curr_month_remain_principal_amount,
                                                 remain_interest_amount=curr_month_remain_interest_amount,
                                                 repaid_repayment_amount=repaid_repayment_amount,
                                                 repaid_principal_amount=repaid_principal_amount,
                                                 repaid_interest_amount=repaid_interest_amount)

            monthly_repayment_list.append(monthly_repayment)
            # 开启新一年
            if current_month == 12:
                yearly_repay = YearlyRepayment(year=current_year, monthly_repayment_list=monthly_repayment_list)
                self.yearly_repayment_list.append(yearly_repay)
                monthly_repayment_list = []
                current_year += 1
                # 重置月份从1开始
                current_month = 1
                continue
            # 月份增加
            current_month += 1



class YearlyRepayment:
    """

    """

    def __init__(self, year: int, monthly_repayment_list: list):
        """

        :param year: 当前年份
        :param monthly_repayment: 月供对象实例的列表
        """
        self.year = year
        self.monthly_repayment_list = monthly_repayment_list
        self._repayment_amount = self._set_repayment_amount()
        self._principal_amount = self._set_principal_amount()
        self._interest_amount = self._set_interest_amount()


    @property
    def repayment_amount(self) -> Decimal:
        """
        getter of repayment_amount，得到当年总还款额
        :return:
        """
        return self._repayment_amount

    def _set_repayment_amount(self) -> Decimal:
        repayment_amount = 0
        for monthly_repayment in self.monthly_repayment_list:
            repayment_amount += monthly_repayment.repayment
        return repayment_amount

    @property
    def principal_amount(self):
        """
        getter of principal_amount，得到当年本金总额
        :return:
        """
        return self._principal_amount

    def _set_principal_amount(self) -> Decimal:
        principal_amount = 0
        for monthly_repayment in self.monthly_repayment_list:
            principal_amount += monthly_repayment.principal
        return principal_amount

    @property
    def interest_amount(self):
        """
        getter of interest_amount，得到当年利息总额
        :return:
        """
        return self._interest_amount

    def _set_interest_amount(self) -> Decimal:
        interest_amount = 0
        for monthly_repayment in self.monthly_repayment_list:
            interest_amount += monthly_repayment.interest
        return interest_amount


class MonthlyRepayment:
    """

    """

    def __init__(self, months: int, month: int, repayment: Decimal, principal: Decimal, interest: Decimal,
                 interest_percentage: Decimal,
                 remain_repayment_amount: Decimal, remain_principal_amount: Decimal, remain_interest_amount: Decimal,
                 repaid_repayment_amount: Decimal,
                 repaid_principal_amount: Decimal, repaid_interest_amount: Decimal):
        """

        :param months: 当前还款期数（第几期还款）
        :param month: 当前月份
        :param repayment: 当月月供
        :param principal: 当月月供中的本金
        :param interest: 当月月供中的利息
        :param interest_percentage: 当月利息占比
        :param remain_repayment_amount: 剩余月供总额
        :param remain_principal_amount: 剩余本金总额
        :param remain_interest_amount: 剩余利息总额
        :param repaid_repayment_amount: 截止此月已累计还款总额
        :param repaid_principal_amount: 截止此月已累计还本金总额
        :param repaid_interest_amount: 截止此月已累计还利息总额
        """
        self.months = months
        self.month = month
        self.repayment = repayment
        self.principal = principal
        self.interest = interest
        self.interest_percentage = interest_percentage
        self.remain_repayment_amount = remain_repayment_amount
        self.remain_principal_amount = remain_principal_amount
        self.remain_interest_amount = remain_interest_amount
        self.repaid_repayment_amount = repaid_repayment_amount
        self.repaid_principal_amount = repaid_principal_amount
        self.repaid_interest_amount = repaid_interest_amount

    def get_month(self) -> str:
        months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct',
                  11: 'Nov', 12: 'Dec'}
        return months[self.month]


def main():
    # 第一次还款日期
    first_payment = datetime(year=2019, month=1, day=3)
    # 基准利率
    base_interest_rate = Decimal('5.635')
    mortgage = Mortgage(total_principal=70, period=30, base_interest_rate=base_interest_rate,
                        first_payment=first_payment)
    mortgage.calculate_equal_installments()
    # show(mortgage)
    plt(mortgage)


def plt(mortgage: Mortgage):
    principal = []
    interest = []
    interest_percentage = []
    remain_repayment_amount = []
    remain_principal_amount = []
    remain_interest_amount = []
    repaid_repayment_amount = []
    repaid_principal_amount = []
    repaid_interest_amount = []
    for i in mortgage.yearly_repayment_list:
        for n in i.monthly_repayment_list:
            principal.append(n.principal)
            interest.append(n.interest)
            interest_percentage.append(n.interest_percentage)
            remain_repayment_amount.append(n.remain_repayment_amount)
            remain_principal_amount.append(n.remain_principal_amount)
            remain_interest_amount.append(n.remain_interest_amount)
            repaid_repayment_amount.append(n.repaid_repayment_amount)
            repaid_principal_amount.append(n.repaid_principal_amount)
            repaid_interest_amount.append(n.repaid_interest_amount)

    pl.rcParams['font.sans-serif'] = ['FangSong']  # 指定默认字体
    pl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
    x = [i for i in range(1, 361)]  # Make x, y arrays for each graph

    # pl.plot(x, principal, color='r', label='本金')# use pylab to plot x and y
    # pl.plot(x, interest, color='g', label='利息')
    # pl.plot(x, interest_percentage, color='g', label='利息占比')
    # pl.plot(x, remain_repayment_amount, color='b', label='剩余月供')
    # pl.plot(x, remain_principal_amount, color='c', label='剩余本金')
    # pl.plot(x, remain_interest_amount, color='m', label='剩余利息')
    pl.plot(x, repaid_repayment_amount, color='y', label='已还月供')
    pl.plot(x, repaid_principal_amount, color='k', label='已还本金')
    pl.plot(x, repaid_interest_amount, color='burlywood', label='已还利息')

    pl.title('月供本金与利息变化趋势')  # give plot a title
    pl.xlabel('期数')  # make axis labels
    pl.ylabel('月供')

    pl.legend(loc='best')
    pl.show()  # show the plot on the screen


def print_result(mortgage: Mortgage):
    print('-----------------------------------')
    print('月供总额（Interest amount）： %.2f ' % mortgage.repayment_amount)
    print('利息总额（Repayment amount）： %.2f ' % mortgage.interest_amount)
    for i in mortgage.yearly_repayment_list:
        print('-----------------------------------')
        print("{0}年：".format(i.year))
        print("当年月供总额：%.2f" % i.repayment_amount)
        print("当年本金总额：%.2f" % i.principal_amount)
        print("当年利息总额：%.2f" % i.interest_amount)
        print('-----------------------------------')
        principal = []
        interest = []
        interest_percentage = []
        remain_repayment_amount = []
        remain_principal_amount = []
        remain_interest_amount = []
        repaid_repayment_amount = []
        repaid_principal_amount = []
        repaid_interest_amount = []
        for n in i.monthly_repayment_list:
            print("期数：{0}".format(n.months))
            print("月份：{0}".format(n.get_month()))
            print("当月月供：%.2f" % n.repayment)
            print("当月本金：%.2f" % n.principal)
            print("当月利息：%.2f" % n.interest)
            print("当月利息占比：%.2f%%" % n.interest_percentage)
            print("剩余月供：%.2f" % n.remain_repayment_amount)
            print("剩余本金：%.2f" % n.remain_principal_amount)
            print("剩余利息：%.2f" % n.remain_interest_amount)
            print("累计月供总额：%.2f" % n.repaid_repayment_amount)
            print("累计本金总额：%.2f" % n.repaid_principal_amount)
            print("累计利息总额：%.2f" % n.repaid_interest_amount)


if __name__ == '__main__':
    main()

