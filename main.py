from http.client import HTTPException
import random
from models.campaign import CampaignDB
from models.state import StateDB, StateUpdate
import numpy as np
import matplotlib.pyplot as plt
import copy
from utils.db_connector import DBConnector, Collections
from bson.binary import Binary
import pickle

connector = DBConnector()

class AI(object):
    def __init__(self, id, env, initial_q, initial_visits):
        k = connector.collection(Collections.AI).find_one({"id": env.id}) #mapping State to AI | State.id must be equal to AI.id
        #IF AI() has not been created
        if k is None:
            self.id = id,
            self.env = env
            self.initial_q = initial_q
            self.initial_visits = initial_visits

            self.q_values = np.ones(self.env.k_arms) * self.initial_q
            self.arm_counts = np.ones(self.env.k_arms) * self.initial_visits
            self.arm_rewards = np.zeros(self.env.k_arms)

        # If we alreaddy created AI(), update values from DB 
        else:
            self.id = k["id"],
            self.env = env
            self.initial_q = k["initial_q"]
            self.initial_visits = k["initial_visits"]

            self.q_values = pickle.loads(k["q_values"])
            self.arm_counts = pickle.loads(k["arm_counts"])
            self.arm_rewards = pickle.loads(k["arm_rewards"])

    def act(self):
        arm = np.argmax(self.q_values)
        reward = self.env.take_action(arm, self.q_values)
        self.arm_counts[arm] = self.arm_counts[arm] + 1
        for arm in range(self.env.k_arms):
            self.arm_rewards[arm] = self.arm_rewards[arm] + reward[arm]
            self.q_values[arm] = self.q_values[arm] + (
                1 / self.arm_counts[arm]
            ) * (reward[arm] - self.q_values[arm])
        """
        Storing everything into database
        """
        cam = [] # Crate a list with campaign Id
        for campaign in self.env.campaigns:
            cam.append(campaign.id) 
        # Mapping fields and validating input
        state_update = StateUpdate(
            id=self.env.id,
            budget=self.env.budget,
            time=self.env.time,
            campaigns=cam,
            current_time=self.env.current_time,
            current_budget=self.env.current_budget,
            history=self.env.history,
            budget_allocation=self.env.budget_allocation,
            remaining=self.env.remaining,
            step=self.env.step,
            k_arms=self.env.k_arms,
            stopped=self.env.stopped
        )
        print(state_update)
        # Updating data 
        connector.collection(Collections.STATE).replace_one(
            {"id": self.env.id}, state_update.dict()
        )
        # If there is no AI() created, insert directly to database --> No validation here
        if connector.collection(Collections.AI).find_one({"id": self.env.id}) is None:
            connector.collection(Collections.AI).insert_one({
                "id": self.env.id,
                "initial_q": self.initial_q,
                "initial_visits": self.initial_visits,
                "q_values": Binary(pickle.dumps(self.q_values, protocol=2), subtype=128),
                "arm_counts": Binary(pickle.dumps(self.arm_counts, protocol=2), subtype=128),
                "arm_rewards": Binary(pickle.dumps(self.arm_rewards, protocol=2), subtype=128),
            })
        # If the table has been updated --> replace it 
        else:
            ai = {
                "id": self.env.id,
                "initial_q": self.initial_q,
                "initial_visits": self.initial_visits,
                "q_values": Binary(pickle.dumps(self.q_values, protocol=2), subtype=128),
                "arm_counts": Binary(pickle.dumps(self.arm_counts, protocol=2), subtype=128),
                "arm_rewards": Binary(pickle.dumps(self.arm_rewards, protocol=2), subtype=128),
            }
            connector.collection(Collections.AI).replace_one(
                {"id": self.env.id}, ai
            )
        return 'success'

class Campaign:
    def __init__(self,id,budget,spent,conversion_value):
        self.id = id    
        self.budget = budget # daily budget
        self.spent = [spent] #spent across time steps
        self.conversion_value = [conversion_value] #conversion value across time steps  

    def update(self, new_spent, new_value):
        """
        updates self.converion_value and self.spent with new data
        """
        self.spent.append(new_spent)
        self.conversion_value.append(new_value)
        connector.collection(Collections.CAMPAIGN).update_one({
            "id": self.id
        },
        {
            "$set":{
                "spent": self.spent,
                "conversion_value": self.conversion_value
            }
        })

    def change_budget(self, increment):
        # increment debe ser un valor numerico para editar el ( daily budget )
        self.budget = self.budget + increment
        connector.collection(Collections.CAMPAIGN).update_one({
            "id": self.id
        },
        {
            "$set":{
                "budget": self.budget
            }
        })

class State(Campaign):
    """
    The class state will contain all the methods and attributes required to interact with the environment.
    """
    def __init__(
        self, state:StateDB, initial_allocation=None
    ):
        self.id = state.id # We assign an ID to deal with multiple CampaignGroup
        self.budget = state.budget # We set up a total budget
        self.time = state.time # We set up a total number of time steps to distribute the budget
        """
        We create a list that will contain campaign objects specified by ID
        """
        d = [] 
        for campaign in state.campaigns:
            d.append(
                CampaignDB(
                    **(
                        connector.collection(Collections.CAMPAIGN).find_one(
                            {"id": campaign}
                        )
                    )
                )
            )
        self.campaigns = d # we store that campaigns 
        self.current_time = state.current_time  # We initialize current time 
        self.current_budget = state.current_budget #TODO 
        self.history = state.history # We create a dictionary with key: current_time value: budget_distribution
        self.budget_allocation = state.budget_allocation # We create a dictionary with key: campaign ID value: % budget allocation
        self.remaining = state.remaining # We create a variable to keep track of the remaining budget
        self.step = state.step # Step represent the freedom of action. The % a campaign budget can be changed in 1 timestep. 
        self.k_arms = state.k_arms # K-arms represent campaigns 
        self.stopped = state.stopped # Stopped is a list of campaigns that have been stopped 

        self.timestep = 12 # Number of hours of each time step. 
        """
        We call initial_allocation to distribute budget proportionally if the user didn't provide an initial distribution 
        """
        if initial_allocation == None and state.current_time == 0:
            self.initial_allocation()
        else:
            if initial_allocation:
                for campaign in d:
                    self.budget_allocation[str(campaign.id)] = initial_allocation[
                        campaign.id
                    ]
    @staticmethod
    def get_state(budget_allocation):
        """
        returns a tuple (0.33,0.33,0.33) at current time step. 
        """
        return tuple(budget_allocation.values())

    def initial_allocation(self):
        """
        We distribute budget proportionally. 
        """
        for campaign in self.campaigns:
            self.budget_allocation[str(campaign.id)] = round(
                1 / len(self.campaigns), 8
            )
        b = copy.deepcopy(self.budget_allocation)
        self.history[str(self.current_time)] = [b, self.get_reward()]
        self.allocate_budget()

    def next_timestamp(self):
        """
        We move time forward, if there is no Budget Left, we stop. 
        """
        self.current_time += 1
        self.remaining -= self.current_budget
        if self.remaining <= 0:
            connector.collection(Collections.AI).delete_one({"id": self.id})
            raise HTTPException("No budget left")
        # increase the capacity of an agent to take significant budget decisions
        self.step *= 1.001

    def get_reward(self):
        """
        Returns a normalized distribution for rewards, based on purchase conversion value. 
        """
        if self.current_time == 0:
            return list(np.zeros(len(self.budget_allocation)))
        rewards = []
        for campaign in self.campaigns:
            rewards.append(campaign.conversion_value[-1])
        if any(rewards) == 0:
            return rewards
        else:
            norm = [float(i)/sum(rewards) for i in rewards] #normalize rewards 
            # print(f'The rewards at timestamp {self.current_time} is {rewards}')
            return norm

    def take_action(self, arm, q_values):
        """
        Takes an action given chosen arm ( campaign to be increased ) and q_values 
        """
        #if it is timestep 0, just wait. 
        if self.current_time < 1:
            print('AI still has no data so no action taken(( ')
        else:
            print(f'AI is increasing budget of campaign {arm} ))')
            self.act2(arm,q_values) # calls act2 action policy 2 ( 1 was shit )
        """
        we have a new baby, a new budget distribution. 
        now we want to store the new baby in self.history 
        wait for its rewards, 
        allocate budget and move time forward. 
        """
        b = copy.deepcopy(self.budget_allocation)
        rewards = self.get_reward() # we compute rewards
        self.history[str(self.current_time)] = [b,rewards] # store previous distribution
        print(f'Current state: {self.budget_allocation} at timestamp {self.current_time}')
        self.allocate_budget() # allocate this new budget distribution
        self.next_timestamp() # move time forward
        return rewards # return current rewards to the AI()

    def act2(self, arm, q_values):
        """
        Given a chosen campaign, change budget distribution. 
        My policy is to increase with step % campaigns[arm]
        and via some stochastic process based on q_values
        determine the decreasing arm. 
        Note: if you want to increase a campaign +1%, 
        then you also need to apple -1% to another one
        we'll call it, decreasing arm. 
        """
        population = list(range(len(self.campaigns)))
        step = self.step
        temp_budget = copy.deepcopy(self.budget_allocation)
        temp_budget[str(arm)] += step
        q_values = q_values.tolist()
        """
        stochastic process to choose and decrease another campaign 
        """
        # SOLUTION TO BUG ID 7
        # print(f"---{len(population)-len(self.stopped)}")
        # time.sleep(0.01)
        if len(population) - len(self.stopped) == 1:
            temp_budget[str(arm)] = 1
        else:
            # if we have no data, randomly decrease an campaign
            if all(v == 0 for v in q_values):
                dec = random.randint(0, len(self.campaigns) - 1)
                if dec != arm:
                    temp_budget[str(dec)] -= step
                else:
                    while dec == arm:
                        dec = random.randint(0, len(self.campaigns) - 1)
                    temp_budget[str(dec)] -= step
            # if we have data, take a stochastic approach
            else:
                norm = [float(i) / sum(q_values) for i in q_values]
                decrease_prob = [1 - p for p in norm]
                # print(f'norm is {norm}')
                # print(f'population is {population}')
                dec = int(
                    random.choices(population, weights=decrease_prob, k=1)[0]
                )
                # we could test another action policy where the chosen arm would be also subject to a decrease,
                # that would result in no action, I'll ignore that option
                if dec != arm and dec not in self.stopped:
                    # TODO SOLUTION OF BUG 1
                    if temp_budget[str(dec)] < step:
                        temp_budget[str(arm)] -= temp_budget[str(dec)]
                        # temp_budget[arm] -= step
                        temp_budget[str(dec)] = 0
                        print(
                            f"##### Campaign {dec} was stopped completely ###"
                        )
                        # TODO delete campaign from the state ( make it ignore it )
                        self.stopped.append(dec)
                    else:
                        temp_budget[str(dec)] -= step
                else:
                    while True:
                        dec = int(
                            random.choices(
                                population, weights=decrease_prob, k=1
                            )[0]
                        )
                        if dec == arm:
                            continue
                        if dec in self.stopped:
                            continue
                        else:
                            break
                    # SOLUTION OF BUG 1
                    if temp_budget[str(dec)] < step:
                        temp_budget[str(arm)] -= temp_budget[str(dec)]
                        temp_budget[str(arm)] -= step
                        temp_budget[str(dec)] = 0
                        print(
                            f"##### Campaign {dec} was stopped completely ###"
                        )
                        self.stopped.append(dec)
                    else:
                        temp_budget[str(dec)] -= step
                print(
                    f"Ai has decreased campaign {dec} given probs {decrease_prob}"
                )
        # round the budget to avoid RuntimeWarning: invalid value encountered in double_scalars
        for campaign in temp_budget:
            temp_budget[str(campaign)] = round(temp_budget[str(campaign)], 8)
        """
        validate that the budget is corrent before updating it
        """
        if self.validate_budget(temp_budget):
            # update budget
            self.budget_allocation = temp_budget
        else:
            print(f"Chosen arm: {arm}, Stopped Campaigns: {self.stopped}")
            raise Exception(f"Budget is not valid, act2 policy has failed, Failed budget is {temp_budget}") #TODO --> why you did not use HTTPException

    def allocate_budget(self):
        # turns a distribution into a daily value
        # X =  number of time steps in a day 
        # campaign daily budget = current budget * campaign%allocation * X
        
        #TODO --> i am not sure this is saving into database
        x = 24/self.timestep
        for campaign in self.campaigns:
            campaign.budget = round(
                self.current_budget * self.budget_allocation[str(campaign.id)]*x, 8
            )
            connector.collection(Collections.CAMPAIGN).update_one(
                {"id": campaign.id},
                {
                    "$set":{
                        "budget": campaign.budget
                    }
                }
            )

    @staticmethod
    def validate_budget(budget_allocation):
        """
        here we validate budgets we tolerate 
        a minimum of 95%
        a maximum of 102.5%
        -- +2.5% ===> maximum overspent allowed.  
        """
        total = 0
        for campaign in budget_allocation.values():
            if campaign > 1:
                return False
            elif campaign < 0:
                return False
            else:
                total += campaign
        total = round(total, 4)
        if total > 0.95 and total <= 1.025:
            # it is better that we spend less than more.
            return True
        else:
            return False
