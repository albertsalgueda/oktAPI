from main import *

def budget_printer(campaign_group):
    i=0
    budget = campaign_group.budget_allocation
    for campaign in budget:
        print(f'{campaign} has a {round(budget[campaign]*100,4)}% of the current budget, which is {campaign_group.campaigns[i].budget}')
        print(f'{campaign} has {campaign_group.campaigns[i].impressions} impressions')
        print(f'{campaign} has {campaign_group.campaigns[i].conversions} conversions')
        print(f'{campaign} has {campaign_group.campaigns[i].roi} ROI')
        i +=1

print('Welcome to the simulation of Oktopus ;)')
print('We created group of 3 init campaigns for you already')

campaign1 = Campaign(0,0,0,0,0,0)
campaign2 = Campaign(1,0,0,0,0,0)
campaign3 = Campaign(2,0,0,0,0,0)
campaigns = [campaign1,campaign2,campaign3]

budget = int(input('Introduce total budget: '))
time = int(input('Introduce the number of timestamps: '))
inital_allocation = [0.25,0.25,0.5]

campaign_group = State(budget,time,campaigns,inital_allocation)

artificial_intelligence = AI(campaign_group,10,10)

while campaign_group.remaining > 0:
    print('#############################################')
    print(f'Budget at timestamp {campaign_group.current_time} is {campaign_group.current_budget}')
    budget_printer(campaign_group)
    ## /next
    action = artificial_intelligence.act()
    for campaign in campaign_group.campaigns:
        print(f'Introduce new data for campaign {campaign.id}')
        data = str(input("new Impresions, new Conversions and new ROI respectively separated with a comma: "))
        data = data.split(',')
        campaign.update(data[0],data[1],data[2])
    i = input("Ready for the /next time step?")
    print(f'Remaining budget: {campaign_group.remaining}')

print('Optimization finished, thanks for trusting Oktopus')