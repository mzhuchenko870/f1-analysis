```mermaid
erDiagram
    seasons {
        int year PK
    }
    circuits {
        int circuitId PK
        string name
        string country
    }
    races {
        int raceId PK
        int year FK
        int circuitId FK
        string name
        date date
    }
    drivers {
        int driverId PK
        string forename
        string surname
        string nationality
    }
    constructors {
        int constructorId PK
        string name
        string nationality
    }
    status {
        int statusId PK
        string status
    }
    results {
        int resultId PK
        int raceId FK
        int driverId FK
        int constructorId FK
        int statusId FK
        int positionOrder
        float points
    }
    qualifying {
        int qualifyId PK
        int raceId FK
        int driverId FK
        int constructorId FK
        string q1
        string q2
        string q3
    }
    lap_times {
        int raceId FK
        int driverId FK
        int lap
        string time
    }
    pit_stops {
        int raceId FK
        int driverId FK
        int stop
        int lap
        string duration
    }
    driver_standings {
        int driverStandingsId PK
        int raceId FK
        int driverId FK
        float points
        int position
    }
    constructor_standings {
        int constructorStandingsId PK
        int raceId FK
        int constructorId FK
        float points
        int position
    }

    seasons ||--o{ races : "year"
    circuits ||--o{ races : "circuitId"
    races ||--o{ results : "raceId"
    races ||--o{ qualifying : "raceId"
    races ||--o{ lap_times : "raceId"
    races ||--o{ pit_stops : "raceId"
    races ||--o{ driver_standings : "raceId"
    races ||--o{ constructor_standings : "raceId"
    drivers ||--o{ results : "driverId"
    drivers ||--o{ qualifying : "driverId"
    drivers ||--o{ lap_times : "driverId"
    drivers ||--o{ pit_stops : "driverId"
    drivers ||--o{ driver_standings : "driverId"
    constructors ||--o{ results : "constructorId"
    constructors ||--o{ qualifying : "constructorId"
    constructors ||--o{ constructor_standings : "constructorId"
    status ||--o{ results : "statusId"
```
