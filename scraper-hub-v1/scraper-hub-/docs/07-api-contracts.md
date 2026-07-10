# API Contracts

## Admin/source management
- `GET /api/v1/sources`
  - Response: Array of source objects
    ```json
    [
      {
        "id": 1,
        "name": "Source Name",
        "category": "telecom",
        "base_url": "https://example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ]
    ```
- `POST /api/v1/sources`
  - Request:
    ```json
    {
      "name": "Source Name",
      "category": "telecom",
      "base_url": "https://example.com"
    }
    ```
  - Response: Created source object (same as above)
- `PATCH /api/v1/sources/{id}`
  - Request: Partial source object (same fields as POST, all optional)
  - Response: Updated source object
- `POST /api/v1/sources/{id}/run`
  - Response:
    ```json
    {
      "message": "Scrape initiated for source 1"
    }
    ```

## Manual scraping
- `POST /api/v1/manual-scrape`
  - Request:
    ```json
    {
      "url": "https://example.com/page",
      "category": "telecom",
      "extractor_type": "auto",
      "store_result": true
    }
    ```
  - Response (when store_result=true):
    ```json
    {
      "message": "Page scraped and processed successfully",
      "snapshot_id": 1,
      "url": "https://example.com/page",
      "content_length": 12345,
      "extracted_records_count": 3,
      "extracted_records": [
        {
          "id": 1,
          "entity_name": "Vodafone",
          "category": "telecom",
          "subcategory": "mobile",
          "title": "Unlimited Plan",
          "price_value": 25.0,
          "price_currency": "GBP",
          "captured_at": "2024-01-01T00:00:00Z"
        }
      ]
    }
    ```
  - Response (when store_result=false):
    ```json
    {
      "message": "Page scraped successfully",
      "url": "https://example.com/page",
      "content_length": 12345
    }
    ```

## Records
- `GET /api/v1/records`
  - Query parameters:
    - `category` (optional): Filter by category (telecom, banking)
    - `entity_name` (optional): Filter by entity name
    - `subcategory` (optional): Filter by subcategory
    - `limit` (optional): Maximum records to return (default 100, max 1000)
    - `offset` (optional): Number of records to skip (default 0)
  - Response: Array of record objects
    ```json
    [
      {
        "id": 1,
        "snapshot_id": 1,
        "entity_name": "Vodafone",
        "category": "telecom",
        "subcategory": "mobile",
        "title": "Unlimited Plan",
        "item_name": null,
        "description": "Unlimited calls and texts",
        "price_value": 25.0,
        "price_currency": "GBP",
        "billing_period": "month",
        "unit_value": 100.0,
        "unit_type": "GB",
        "eligibility": null,
        "effective_date": null,
        "captured_at": "2024-01-01T00:00:00Z",
        "source_url": "https://vodafone.co.uk/plans",
        "confidence_score": 0.8
      }
    ]
    ```
- `GET /api/v1/records/{id}`
  - Response: Single record object (same structure as above)

## Job runs
- `GET /api/v1/jobs`
- `GET /api/v1/jobs/{id}`

## Integrations
- `GET /api/v1/integrations/targets`
- `POST /api/v1/integrations/targets`
- `POST /api/v1/integrations/publish/{record_id}`
- `POST /api/v1/integrations/publish/batch`