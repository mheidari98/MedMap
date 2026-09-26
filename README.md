# MedMap-Iran 🏥

Interactive map of medical centers under contract with **SOS Pasargard insurance** in Iran (مراکز خدمات درمانی که با بیمه SOS پاسارگارد قرارداد دارند), operated through [Iran Assistance / کمک‌رسان ایران](https://iranassistance.com/medical-centers), which publishes the source directory of contracted centers.

Live map: https://mheidari98.github.io/MedMap/

## Features

- 🗺️ Interactive map visualization of medical centers
- 🏷️ Filter by province, center type, and name
- 📍 Location-based search
- 🌙 Multiple map styles
- 🔄 Weekly updated data

## Quick Start

### Using Docker

```bash
docker compose up --build
```

Visit `http://localhost:8050` in your browser.

### Manual Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Update data:
```bash
python scraper.py
```

3. Run dashboard:
```bash
python dashboard.py
```


## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

MIT License
