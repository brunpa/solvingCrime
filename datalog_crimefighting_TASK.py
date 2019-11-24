#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 14:38:21 2017

@author: tugg
update: vissejul, bachmdo2, stdm (Nov 27, 2018)
"""
import pandas as pa
from pyDatalog import pyDatalog

# ---------------------------------------------------------------------------
# Social graph analysis:
# work through this code from top to bottom (in the way you would use a R or Jupyter notebook as well...) and write datalog clauses
# and python code in order to solve the respective tasks. Overall, there are 7 tasks.
# ---------------------------------------------------------------------------
calls = pa.read_csv('calls.csv', sep='\t', encoding='utf-8')
texts = pa.read_csv('texts.csv', sep='\t', encoding='utf-8')

suspect = 'Quandt Katarina'
company_Board = ['Soltau Kristine', 'Eder Eva', 'Michael Jill']

pyDatalog.create_terms('knows', 'has_link', 'board_member', 'has_path', 'short_path', 'short_path', 'COUNTER',
                       'COUNTER2', 'many_more_needed', 'X', 'Y', 'Z',
                       'P', 'P2', 'DATE', 'DATE2', 'TP', 'TP2', 'paths')
pyDatalog.clear()  # clears all facts and clauses

# First, treat calls as simple social links (denoted as knows), that have no date
for i in range(0, 150):
    +knows(calls.iloc[i, 1], calls.iloc[i, 2])

# Create predicate to check if a person is a member of the board
for i in range(len(company_Board)):
    +board_member(company_Board[i])

# Task 1: Knowing someone is a bi-directional relationship -> define the predicate accordingly
knows(X, Y) <= knows(Y, X)
print("\nWho knows the suspect?\n")
print(knows(suspect, Y))


# Task 2: Define the predicate has_link in a way that it is true if a connection exists (path of people knowing the next link)
has_link(X,Y) <= knows(X,Y) # direct relationship
has_link(X,Y) <= knows(X,Z) & has_link(Z,Y) & (X!=Y)

print("\nWho has a link with the suspect?\n")
print(has_link(suspect, Y))
print("\nWho has a link with the suspect and is part of the company board?\n")
print(has_link(suspect, Y) & (board_member(Y)))

# Hints:
#   check if your predicate works: at least 1 of the following asserts should be true (2 if you read in all 150 communication records)
#   (be aware of the unusual behaviour that if an assert evaluates as true, an exception is thrown)
#assert (has_link('Quandt Katarina', company_Board[0]) == ())
#assert (has_link('Quandt Katarina', company_Board[1]) == ())
#assert (has_link('Quandt Katarina', company_Board[2]) == ())


# Task 3: You already know that a connection exists; now find the concrete paths between the board members and the suspect
# Hints:
#   if a knows b, there is a path between a and b
#   (X._not_in(P2)) is used to check whether x is not in path P2
#   (P==P2+[Z]) declares P as a new path containing P2 and Z
# has_path(X, Y, P) <= knows(X, Y) & (P == [])  # direct path
# has_path(X, Y, P) <= has_path(X, Z, P2) & knows(Z, Y) & (P == P2 + [Y]) & (X._not_in(P2)) & (Y._not_in(P2)) & (X != Y)
has_path(X, Y, P) <= knows(X, Y) & (P == [])
has_path(X, Y, P) <= has_path(X, Z, P2) & knows(Z, Y) & (Y._not_in(P2)) & (X != Y) & (P == P2 + [Y])
# print("\nPaths between board members and suspect (Quandt Katarina)\n")
# print(has_path(suspect,Y,P) & board_member(Y)) TODO: Aufruf funktioniert nicht in print resp. dauert extrem lange - wohl aufgrund der Eingabemenge.


# Task 4: There are too many paths. We are only interested in short paths.
# Find all the paths between the suspect and the company board that contain five people or less
short_path(X, Y, P, COUNTER) <= knows(X, Y) & (P == []) & (COUNTER == 2)
short_path(X, Y, P, COUNTER) <= short_path(X, Z, P2, COUNTER2) & knows(Z, Y) & (Y._not_in(P2)) & (X != Y) & (
            P == P2 + [Z]) & (COUNTER == COUNTER2 + 1) & (COUNTER2 < 5)
print("\nWhat are the paths with less than 5 persons between board members and the suspect?\n")
print(short_path(suspect, Y, P, COUNTER) & board_member(Y))
# ---------------------------------------------------------------------------
# Call-Data analysis:
# Now we use the text and the calls data together with their corresponding dates
# ---------------------------------------------------------------------------
date_board_decision = '12.2.2017'
date_shares_bought = '23.2.2017'
pyDatalog.create_terms('called,texted')
pyDatalog.clear()  # clears all facts and clauses

for i in range(0, 150):  # calls
    +called(calls.iloc[i, 1], calls.iloc[i, 2], calls.iloc[i, 3])

for i in range(0, 150):  # texts
    +texted(texts.iloc[i, 1], texts.iloc[i, 2], texts.iloc[i, 3])

called(X, Y, Z) <= called(Y, X, Z)  # calls are bi-directional

# Create predicate to check if a person is a member of the board
for i in range(len(company_Board)):
    +board_member(company_Board[i])


# Task 5: Again we are interested in links, but this time a connection is only valid if the links are descending in date;
#         find out who could have actually sent the information by adding this new restriction
# Hints:
#   You are allowed to naively compare the dates lexicographically using ">" and "<";
#   it works in this example (but is evil in general)

# Direct link
has_link(X, Y, DATE) <= called(X, Y, DATE) & board_member(Y) & (DATE >= date_board_decision) & (
            DATE <= date_shares_bought)
has_link(X, Y, DATE) <= texted(Y, X, DATE) & board_member(Y) & (DATE >= date_board_decision) & (
            DATE <= date_shares_bought)

#
has_link(Y, Z, DATE) <= has_link(X, Z, DATE2) & called(X, Y, DATE) & (DATE2 <= DATE) & (DATE <= date_shares_bought) & (
            X != Y) & (Z != Y)
has_link(Y, Z, DATE) <= has_link(X, Z, DATE2) & texted(X, Y, DATE) & (DATE2 <= DATE) & (DATE <= date_shares_bought) & (
            X != Y) & (Z != Y)
print("\nThe links between the suspect and the members of the company board in descending DATE order:\n")
print(has_link(suspect, Y, DATE))


# Task 6: Find all the communication paths that lead to the suspect (with the restriction that the dates have to be ordered correctly)

# Path between two persons (empty path)
paths(X, Y, P, DATE, TP) <= called(X, Y, DATE) & (X != Y) & (P == []) & (TP == [DATE]) & (
            DATE >= date_board_decision) & (DATE <= date_shares_bought)
paths(Y, X, P, DATE, TP) <= texted(X, Y, DATE) & (X != Y) & (P == []) & (TP == [DATE]) & (
            DATE >= date_board_decision) & (DATE <= date_shares_bought)

# Expanded Path
(paths(X, Y, P, DATE, TP)) <= (paths(X, Z, P2, DATE2, TP2)) & texted(Y, Z, DATE) & (P == P2 + [Z]) & (
            TP == TP2 + [DATE]) & (DATE <= DATE2) & (DATE >= date_board_decision) & (Y._not_in(P2)) & (X != Y)
(paths(X, Y, P, DATE, TP)) <= (paths(X, Z, P2, DATE2, TP2)) & called(Y, Z, DATE) & (P == P2 + [Z]) & (
            TP == TP2 + [DATE]) & (DATE <= DATE2) & (DATE >= date_board_decision) & (Y._not_in(P2)) & (X != Y)

print("\nThe path between suspect and board members:\n")
print(paths(suspect, Y, P, DATE, TP) & board_member(Y))


# Final task: after seeing this information, who, if anybody, do you think gave a tip to the suspect?
print("\nAfter seeing this information, who, if anybody, do you think gave a tip to the suspect?\n")
print("=> Eder Eva")

# General hint (only use on last resort!):
#   if nothing else helped, have a look at https://github.com/pcarbonn/pyDatalog/blob/master/pyDatalog/examples/graph.py
