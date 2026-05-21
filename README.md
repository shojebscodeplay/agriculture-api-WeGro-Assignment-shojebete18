# Agriculture API — WeGro Technologies Ltd. Assignment

A production-ready REST API built with **FastAPI**, **Pandas**, and **MySQL** to analyze agricultural farm and crop performance data across Bangladesh.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Framework | FastAPI |
| Database | MySQL |
| DB Driver | SQLAlchemy + PyMySQL |
| Data Processing | Pandas |
| Server | Uvicorn |
| Python | 3.12+ |

---

## Project Structure

```
agriculture-api/
├── app/
│   ├── main.py               # FastAPI app entry point
│   ├── core/
│   │   ├── database.py       # DB connection + fetch_data()
│   │   ├── exceptions.py     # Custom error handlers
│   │   └── enums.py          # Valid filter values (Enum)
│   ├── routers/
│   │   ├── farms.py          # Farm endpoints
│   │   ├── crops.py          # Crop endpoints
│   │   └── markets.py        # Market endpoints
│   └── services/
│       ├── farm_service.py   # Farm business logic
│       ├── crop_service.py   # Crop business logic
│       └── market_service.py # Market business logic
├── .env                      # DB credentials (not committed)
├── .env.example              # Example env file
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/shojebscodeplay/agriculture-api-WeGro-assignment.git
cd agriculture-api-WeGro-assignment
```

### 2. Create virtual environment and install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root directory:

```env
HOST=your_mysql_host
PORT=3306
USER=your_username
PASSWORD=your_password
DB=agriculture_db
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

### 5. Open API docs

```
http://localhost:8000/docs
```

---

## API Endpoints

### Report 1 — Farm Performance

| Method | Endpoint | Description |
|---|---|---|
| GET | `/farms/summary` | All farms summary with revenue, profit, cost |
| GET | `/farms/{farm_id}/performance` | Single farm detailed breakdown |
| GET | `/farms/top` | Top N farms ranked by profit/revenue/yield |
| GET | `/farms/loss-analysis` | Post-harvest loss analysis |

### Report 2 — Crop & Market Intelligence

| Method | Endpoint | Description |
|---|---|---|
| GET | `/crops/yield-efficiency` | Actual yield vs national benchmark |
| GET | `/crops/seasonal-trend` | Revenue trend by season and year |
| GET | `/markets/price-comparison` | Price comparison across market channels |
| GET | `/crops/quality-breakdown` | Quality grade and pesticide residue distribution |

---

## Filter Reference

| Filter | Accepted Values |
|---|---|
| `region` | Dhaka, Chittagong, Sylhet, Rajshahi, Khulna, Rangpur, Barisal, Mymensingh |
| `farm_type` | Small, Medium, Large, Commercial |
| `crop_category` | Cereal, Vegetable, Fruit, Pulse, Oilseed, Cash Crop, Spice |
| `season` | Spring, Summer, Autumn, Winter |
| `market_type` | Local, Wholesale, Export, Retail, Government Procurement |
| `quality_grade` | A, B, C, D |
| `pesticide_residue` | None, Trace, Low, High |
| `year` | 2022, 2023, 2024 |
| `quarter` | 1, 2, 3, 4 |
| `metric` | profit, revenue, yield |

> Invalid filter values return **HTTP 422** with a clear error message.

---

## Example Requests

```bash
# All farms in Dhaka
GET /farms/summary?region=Dhaka

# Top 5 farms by revenue in Rajshahi
GET /farms/top?metric=revenue&region=Rajshahi&limit=5

# Farm 1 performance for Cereal crops in 2023
GET /farms/1/performance?year=2023&crop_category=Cereal

# Crop yield efficiency for Cereals
GET /crops/yield-efficiency?crop_category=Cereal

# Market price comparison for Export markets
GET /markets/price-comparison?market_type=Export

# Quality breakdown for Fruits in Rajshahi
GET /crops/quality-breakdown?crop_category=Fruit&region=Rajshahi
```

---

## Running with Docker

```bash
# Build the image
docker build -t agriculture-api .

# Run the container
docker run -p 8000:8000 --env-file .env agriculture-api
```

---

## Error Handling

| Status Code | Meaning |
|---|---|
| 200 | Success |
| 422 | Invalid filter value |
| 404 | Record not found |
| 500 | Internal server error |

---

## Database Views Used

| View | Description |
|---|---|
| `vw_harvest_full` | All tables joined — main data source |
| `vw_farm_profitability` | Farm-wise profit and loss summary |
| `vw_revenue_by_crop_year` | Revenue grouped by crop and year |
