#GroceryStoreSim.py
#Name: Jacob Oetken
#Date: 4/26/2025
#Assignment: Lab 11


import simpy
import random

#global variables
eventLog = []
waitingShoppers = []
idleTime = 0

def shopper(env, id):
    #a shopper arrives, shops, and gets in line
    arrive = env.now
    items = random.randint(5, 20)
    shoppingTime = items // 2 + random.randint(-1, 1)  #small random fluctuation
    shoppingTime = max(1, shoppingTime)  #ensure at least 1 minute
    yield env.timeout(shoppingTime)
    waitingShoppers.append((id, items, arrive, env.now))

def checker(env):
    #a checker scans items for shoppers or waits  (idle time)
    global idleTime
    while True:
        if len(waitingShoppers) == 0:
            idleTime += 1
            yield env.timeout(1)  #wait 1 minute if no customers and check again
        else:
            customer = waitingShoppers.pop(0)
            items = customer[1]
            checkoutTime = items // 10 + 1  #minimum checkout time of 1 min
            yield env.timeout(checkoutTime)
            eventLog.append((customer[0], customer[1], customer[2], customer[3], env.now))  #log event

def customerArrival(env):
    #new shoppers arrive every random (but averaged) minutes
    customerNumber = 0
    while True:
        customerNumber += 1
        env.process(shopper(env, customerNumber))
        yield env.timeout(random.expovariate(1/2))

def processResults():
    #summarize simulation results
    totalWait = 0
    totalShoppers = 0
    totalItems = 0
    totalShoppingTime = 0
    maxWait = 0

    for e in eventLog:
        waitTime = e[4] - e[3]  #depart time - done shopping time
        totalWait += waitTime
        totalItems += e[1]
        totalShoppingTime += e[3] - e[2]  #done shopping - arrival
        totalShoppers += 1
        if waitTime > maxWait:
            maxWait = waitTime

    avgWait = totalWait / totalShoppers if totalShoppers else 0
    avgItems = totalItems / totalShoppers if totalShoppers else 0
    avgShoppingTime = totalShoppingTime / totalShoppers if totalShoppers else 0

    print("\n--- simulation results ---")
    print(f"total shoppers: {totalShoppers}")
    print(f"average wait time: {avgWait:.2f} minutes")
    print(f"maximum wait time: {maxWait:.2f} minutes")
    print(f"average items purchased: {avgItems:.2f}")
    print(f"average shopping time: {avgShoppingTime:.2f} minutes")
    print(f"total idle time for checkers: {idleTime} minutes")
    print(f"shoppers still waiting: {len(waitingShoppers)}\n")

def main():
    #setup simulation parameters
    numberCheckers = 6  #number of checkers working
    simTime = 240  #total simulation time in minutes (3 hours)

    env = simpy.Environment()

    env.process(customerArrival(env))
    for i in range(numberCheckers):
        env.process(checker(env))

    env.run(until=simTime)
    processResults()

if __name__ == '__main__':
    main()