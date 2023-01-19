#[derive(PartialEq, Clone, Copy)]
enum BType {
    RailwayStation,
    MarketStall,
    PoliceStation,
    PostOffice,
    SmallStore,
    Hospital,
    FireStation,
    SuperStore,
    Pier,
    Dock,
    Quarry,
    SmallFactory,
    LargeFactory,
    Farming,
    NavalDockyard,
    Mills,
    Airbase,
    SupplyHub,
    Reactor,
    ElectricalGeneration,
    Airport,
    House,
    Office,
    MetroStation,
}

struct BuildingInfo {
    wage: f64,
    employees: f64,
    cost: f64,
}

#[derive(Clone, Copy)]
struct Building {
    ty: BType,
    size: u32,
    count: f64,
}

struct Loan {
    amt: f64,
    interest: f64,
}

struct Economy {
    buildings: Vec<Building>,
    loans: Vec<Loan>,
    bal: f64,
}

const INFO: [BuildingInfo; 24] = [
    BuildingInfo { wage: 13.5, employees: 2.0,    cost: 2808.0 },
    BuildingInfo { wage: 11.0, employees: 1.0,    cost: 1144.00 },
    BuildingInfo { wage: 19.6, employees: 3.0,    cost: 6115.20 },
    BuildingInfo { wage: 12.5, employees: 2.0,    cost: 2600.00 },
    BuildingInfo { wage: 11.5, employees: 2.0,    cost: 2392.00 },
    BuildingInfo { wage: 26.0, employees: 3.0,    cost: 8112.00 },
    BuildingInfo { wage: 19.0, employees: 2.0,    cost: 3952.00 },
    BuildingInfo { wage: 12.2, employees: 4.0,    cost: 5075.20 },
    BuildingInfo { wage: 14.0, employees: 1.0,    cost: 1456.00 },
    BuildingInfo { wage: 15.8, employees: 2.0,    cost: 3286.40 },
    BuildingInfo { wage: 11.2, employees: 2.0,    cost: 2329.60 },
    BuildingInfo { wage: 14.5, employees: 6.0,    cost: 9048.00 },
    BuildingInfo { wage: 15.5, employees: 12.0,   cost: 19344.0 },
    BuildingInfo { wage: 18.5, employees: 1.0/162.0,cost: 11.9    },
    BuildingInfo { wage: 15.5, employees: 1.0,    cost: 1612.00 },
    BuildingInfo { wage: 0.0,  employees: 12.0,   cost: 25500.0 },
    BuildingInfo { wage: 17.5, employees: 4.0,    cost: 7280.00 },
    BuildingInfo { wage: 10.5, employees: 1.0,    cost: 1092.00 },
    BuildingInfo { wage: 20.5, employees: 3.0,    cost: 6396.00 },
    BuildingInfo { wage: 12.5, employees: 2.0,    cost: 2600.00 },
    BuildingInfo { wage: 18.0, employees: 0.0,    cost: 69.0    },
    BuildingInfo { wage: 0.0,  employees: 0.0,    cost: 69420.0 },
    BuildingInfo { wage: 18.0, employees: 1.0,    cost: 1872.00 },
    BuildingInfo { wage: 12.9, employees: 1.0,    cost: 1341.60 }
];
const ROI: f64 = 13.0;
const OVERDRAFT_INTEREST: f64 = 0.30;

impl Building {
    fn new_sized(ty: BType, size: u32, count: u32) -> Self {
        Self {
            ty, size, count: count as f64
        }
    }
    
    fn new(ty: BType, count: u32) -> Self {
        Self {
            ty, size: 0, count: count as f64
        }
    }

    fn cost(&self) -> f64 {
        if self.ty == BType::Airport {
            ROI * self.income()
        } else if self.ty == BType::House {
            (match self.size {
                1 => 1500.0,
                2 => 3000.0,
                4 => 6000.0,
                6 => 9000.0,
                _ => unreachable!()
            }) * self.count
        } else {
            INFO[self.ty as usize].cost * self.count
        }
    }

    fn wage(&self) -> f64 {
        INFO[self.ty as usize].wage
    }

    fn employees(&self) -> f64 {
        if self.ty == BType::Airport {
            (self.size as f64) / 20.0 * self.count
        } else {
            INFO[self.ty as usize].employees * self.count
        }
    }

    fn income(&self) -> f64 {
        self.wage() * self.employees() * 8.0
    }
}

impl Economy {
    fn new(buildings: Vec<Building>, bal: f64, loans: Vec<Loan>) -> Self {
        Self {
            buildings, bal, loans
        }
    }

    fn add_building(&mut self, b: Building) {
        self.bal -= b.cost();
        self.buildings.push(b);
    }
    fn add_loan(&mut self, loan: Loan) {
        self.bal += loan.amt;
        self.loans.push(loan);
    }
    fn pay_for_loan(&mut self, idx: usize, amt: f64) {
        self.loans[idx].amt -= amt;
        self.bal -= amt;
    }

    fn employ(&self) -> f64 {
        let mut people = 0.0;
        let mut jobs = 0.0;
        for b in self.buildings.iter() {
            if b.ty == BType::House {
                people += b.size as f64 * b.count;
            } else {
                jobs += b.employees();
            }
        }
        jobs / people
    }
    
    fn income(&self) -> f64 {
        let employment = self.employ();
        let gross: _ = self.buildings.iter().map(|b| b.income()).sum::<f64>();
        if employment > 1.0 {
            gross / employment
        } else {
            gross * employment
        }
    }

    fn day(&mut self) {
        let inc = self.income();
        self.bal += inc;
        if self.bal < 0.0 {
            self.bal += self.bal * OVERDRAFT_INTEREST;
        }

        for l in self.loans.iter_mut() {
            l.amt *= 1.0 + l.interest;
        }
        // println!("Bal: {}, Emp: {}, Inc: {}", self.bal, self.employ(), inc);
    }
}

const N: usize = 10;

fn fitness(to_do: [Vec<Building>; N]) -> f64 {
    let mut eco = Economy::new(
        vec![
            Building::new_sized(BType::House, 4, 7),
            Building::new_sized(BType::Airport, 100, 1),
            Building::new_sized(BType::Airport, 109, 1),
            Building::new(BType::MarketStall, 1),
            Building::new(BType::PoliceStation, 1),
            Building::new(BType::Hospital, 1),
            Building::new(BType::PostOffice, 1),
            Building::new(BType::Office, 9),
            Building::new(BType::Farming, 300),
        ],
        -4118.68,
        vec![
            Loan { amt: 13147.8, interest: 0.042 }
        ]
    );
    eco.day();
    for i in 0..N {
        for b in to_do[i].iter() {
            eco.add_building(*b);
        }
        eco.day();
    }
    eco.income()
}

fn main() {
    
}
