from constants import BType, MONEY_PREFIX
import datetime

def calc_population(data):
    regions = {}
    total_people = 0
    for region in data.regions:
        people = 0
        for building in data.regions[region]:
            if building.btype == BType.HOUSE:
                people += building.size        
        regions[region] = people
        total_people += people
    
    return total_people, regions

def calc_jobs(data):
    regions = {}
    total_jobs = 0
    for region in data.regions:
        jobs = 0
        for building in data.regions[region]:
            if building.btype != BType.HOUSE:
                jobs += building.employees()
        regions[region] = jobs
        total_jobs += jobs

    return total_jobs, regions
        

def calc_employment(data):
    pop, _ = calc_population(data)
    jobs, _ = calc_jobs(data)
    return jobs / pop if pop != 0 else 0

def calc_income(data):
    employment = calc_employment(data)
    gross_income = 0
    regional_income = {}
    reduce_by = lambda i, p: i / p if p >= 1 else i * p
    for region in data.regions:
        region_gross_income = 0
        for building in data.regions[region]:
            region_gross_income += building.income()

        region_income = reduce_by(region_gross_income, employment)
        regional_income[region] = region_income
        gross_income += region_gross_income
    
    income = reduce_by(gross_income, employment)
    return income, regional_income

def calc_bal(data):
    bal = 0
    for t in data.transactions:
        bal += t.compute_amount()
    
    return bal

def calc_industry_income(data):
    industries = {}
    employ = calc_employment(data)
    reduce_by = lambda i, p: i / p if p >= 1 else i * p
    for region in data.regions:
        for building in data.regions[region]:
            if building.BType != HOUSE:
                if not building.name(airports_together=True) in industries:
                    industries[building.name(airports_together=True)] = 0
                industries[building.name(airports_together=True)] += reduce_by(building.income(), employ)

    return industries

def format_date(date):
    return datetime.date.fromisoformat(date).strftime("%d/%m/%Y")

def format_money(amt):
    return f"{MONEY_PREFIX}{amt:.02f}"

