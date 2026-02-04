# Phase 1: Foundation - Implementation Plan

**Feature:** Binance-TH Library Foundation
**Branch:** `feature/phase-01-foundation`
**Created:** 2026-02-04
**Status:** Implementation

---

## Table of Contents

1. [Overview](#overview)
2. [Prompt Used](#prompt-used)
3. [Architecture](#architecture)
4. [Implementation Tasks](#implementation-tasks)
5. [Data Models](#data-models)
6. [Testing Strategy](#testing-strategy)
7. [Success Criteria](#success-criteria)

---

## Overview

### Purpose

Set up the foundational project structure and core infrastructure for the Binance-TH Python library. This phase establishes the project scaffolding, core models, exception hierarchy, and configuration management.

### Key Objectives

1. **Project Structure** - Create comprehensive directory structure following Python best practices
2. **Core Models** - Define all Pydantic models for API requests/responses
3. **Exception Hierarchy** - Implement typed exception classes for error handling
4. **Configuration** - Implement pydantic-settings based configuration
5. **CI/CD Setup** - Configure GitHub Actions for automated testing

### Deliverables

- Complete project directory structure
- All core Pydantic models (enums, market, account, orders)
- Exception hierarchy with error code mapping
- Configuration management with environment variable support
- CI/CD pipeline with GitHub Actions
- Pre-commit hooks for code quality
- Unit tests with >95% coverage for foundation code

---

## Prompt Used

```
🎯 Objective
Execute Phase 1: Foundation for the Binance-TH library project, including planning, scaffolding, and initial infrastructure setup, following all project documentation and workflow requirements.

📋 Context
- The project is a Python async library for Binance-TH, with strict architectural, documentation, and workflow standards.
- All requirements and plans are documented in `docs/plan/binance-th-library-plan.md`.
- The project uses strict type safety, async-first patterns, Pydantic models, and comprehensive error handling.
- The repository is not yet on GitHub; it must be pushed as private first.
- All planning and implementation steps must be documented and committed according to project standards.

🔧 Requirements
- Create a new git branch for this phase.
- Push the repository to GitHub as a private repo before any code changes.
- Carefully read and follow `docs/plan/binance-th-library-plan.md` and reference `docs/plan/PLAN_SCAFFOLDING_TEMPLATE.md`.
- Focus only on Phase 1: Foundation (project structure and core infrastructure).
- Plan all steps before coding; document the plan in markdown at `docs/plan/phase-01/` (include the full prompt used).
- After planning, proceed directly to implementation without further confirmation.
- Update the checklist in `docs/plan/binance-th-library-plan.md` after completing all tasks and tests.
- When finished, create a detailed PR to GitHub with comprehensive commit and PR messages, following `.github/instructions/git-commit.instructions.md`.
- Adhere to all architectural, documentation, and workflow standards in `.github/instructions/`.

📁 Code Context
- docs/plan/binance-th-library-plan.md (main planning and checklist document)
- docs/plan/PLAN_SCAFFOLDING_TEMPLATE.md (reference template for planning)
- docs/plan/phase-01/ (directory for your plan markdown file)
- .github/instructions/ (contains all coding, documentation, and workflow standards)

✅ Expected Output
- A new git branch created for Phase 1.
- The repository pushed to GitHub as private.
- A detailed plan for Phase 1 in markdown at `docs/plan/phase-01/`, including the full prompt used.
- Project structure and core infrastructure implemented per plan and standards.
- All tasks and tests completed, with checklist updated in `docs/plan/binance-th-library-plan.md`.
- A comprehensive PR to GitHub with detailed commit and PR messages.
```

---

## Architecture

### Directory Structure

```
binance-th/
├── .github/
│   ├── workflows/
│   │   └── ci.yml                 # GitHub Actions CI/CD
│   └── instructions/              # Development standards (gitignored)
├── binance_th/                    # Main package
│   ├── __init__.py               # Package exports
│   ├── config.py                 # Configuration management
│   ├── exceptions.py             # Exception hierarchy
│   └── models/                   # Pydantic models
│       ├── __init__.py           # Model exports
│       ├── enums.py              # Enum definitions
│       ├── base.py               # Base model classes
│       ├── market.py             # Market data models
│       ├── account.py            # Account & wallet models
│       └── orders.py             # Order models
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures
│   └── test_models/              # Model tests
│       ├── __init__.py
│       ├── test_enums.py
│       ├── test_market.py
│       ├── test_account.py
│       └── test_orders.py
├── docs/
│   └── plan/
│       └── phase-01/             # Phase 1 planning
├── pyproject.toml                # Project configuration
├── .pre-commit-config.yaml       # Pre-commit hooks
├── .gitignore
├── .python-version
└── README.md
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    binance_th Package                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐ │
│  │   config.py  │   │ exceptions.py│   │     models/      │ │
│  │              │   │              │   │                  │ │
│  │ - Settings   │   │ - Base Error │   │ - enums.py       │ │
│  │ - Env vars   │   │ - API Error  │   │ - base.py        │ │
│  │ - Defaults   │   │ - Auth Error │   │ - market.py      │ │
│  │              │   │ - Rate Limit │   │ - account.py     │ │
│  │              │   │ - Network    │   │ - orders.py      │ │
│  └──────────────┘   └──────────────┘   └──────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Tasks

### Task 1: Project Configuration (pyproject.toml)

**Dependencies:**
- `pydantic>=2.0` - Data validation
- `pydantic-settings>=2.0` - Configuration management
- `python>=3.12` - Modern Python features

**Dev Dependencies:**
- `pytest>=8.0` - Testing framework
- `pytest-asyncio>=0.23` - Async test support
- `pytest-cov>=4.0` - Coverage reporting
- `ruff>=0.1` - Linting and formatting
- `mypy>=1.8` - Type checking
- `pre-commit>=3.0` - Git hooks

### Task 2: Exception Hierarchy

```python
BinanceThError (base)
├── BinanceThAPIError
│   ├── BinanceThRateLimitError (429, 418)
│   ├── BinanceThAuthError (401, 403)
│   ├── BinanceThBadRequestError (400)
│   └── BinanceThServerError (5xx)
├── BinanceThNetworkError
├── BinanceThTimeoutError
├── BinanceThValidationError
└── BinanceThWebSocketError
```

### Task 3: Configuration (BinanceThConfig)

Settings via pydantic-settings:
- API credentials (api_key, api_secret)
- REST/WebSocket URLs
- Timeout and retry settings
- Rate limiting configuration
- Logging settings

### Task 4: Core Enums

- `OrderType`: LIMIT, MARKET, STOP_LOSS, etc.
- `OrderSide`: BUY, SELL
- `OrderStatus`: NEW, FILLED, CANCELED, etc.
- `TimeInForce`: GTC, IOC, FOK
- `KlineInterval`: 1m, 5m, 15m, 1h, etc.
- `SymbolType`: GLOBAL, SITE
- `RateLimitType`: REQUEST_WEIGHT, ORDERS, RAW_REQUESTS
- `RateLimitInterval`: SECOND, MINUTE, HOUR, DAY

### Task 5: Pydantic Models

**Market Data Models:**
- ServerTime
- ExchangeInfo, Symbol, RateLimit
- OrderBook, Trade, AggregateTrade
- Kline, Ticker24hr, PriceTicker, BookTicker

**Account Models:**
- AccountInfo, Balance
- UserTrade, TradeFee
- DepositAddress, DepositRecord
- WithdrawResult, WithdrawRecord
- ListenKey

**Order Models:**
- Order (full order model)
- OrderRequest (for creating orders)
- CancelOrderRequest

---

## Data Models

### Model Design Principles

1. **Response models**: Use `extra="allow"` for forward compatibility
2. **Request models**: Use `extra="forbid"` for strict validation
3. **Critical entities**: Use `extra="forbid"` for balances, orders
4. **Decimal for financials**: Always use Decimal for prices/quantities
5. **Field aliases**: Map API field names to Pythonic names

### Example Model

```python
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class Order(BaseModel):
    """Order model for Binance Thailand API."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    order_id: int = Field(alias="orderId")
    symbol: str
    status: OrderStatus
    side: OrderSide
    order_type: OrderType = Field(alias="type")
    price: Decimal
    orig_qty: Decimal = Field(alias="origQty")
    executed_qty: Decimal = Field(alias="executedQty")
```

---

## Testing Strategy

### Unit Tests

1. **Enum Tests**
   - All enum values defined correctly
   - String conversion works
   - Invalid values raise errors

2. **Model Tests**
   - Validation passes for valid data
   - Validation fails for invalid data
   - Field aliases work correctly
   - Decimal precision maintained
   - Extra fields handled per policy

3. **Exception Tests**
   - All exceptions inherit correctly
   - Error codes mapped properly
   - Error messages are useful

4. **Config Tests**
   - Default values work
   - Environment variables loaded
   - Validation of settings

### Coverage Target

- Overall: >95%
- Models: 100%
- Exceptions: 100%
- Config: 100%

---

## Success Criteria

### Code Quality

- [ ] Zero ruff violations
- [ ] Zero mypy errors (strict mode)
- [ ] All tests passing
- [ ] >95% test coverage
- [ ] 100% type coverage for new code

### Functionality

- [ ] All enums defined per API specification
- [ ] All models validate correctly
- [ ] All exceptions properly typed
- [ ] Configuration loads from env vars
- [ ] Pre-commit hooks work

### Documentation

- [ ] This plan document complete
- [ ] README updated with project overview
- [ ] All public APIs documented

### Integration

- [ ] CI/CD pipeline runs successfully
- [ ] Pre-commit hooks pass
- [ ] Code follows project standards

---

## Implementation Checklist

### Phase 0: Setup (Completed)
- [x] Create git branch: `feature/phase-01-foundation`
- [x] Push repository to GitHub as private
- [x] Create this planning document

### Phase 1: Core Implementation
- [ ] Update pyproject.toml with dependencies
- [ ] Create directory structure
- [ ] Implement exceptions.py
- [ ] Implement config.py
- [ ] Implement models/enums.py
- [ ] Implement models/base.py
- [ ] Implement models/market.py
- [ ] Implement models/account.py
- [ ] Implement models/orders.py
- [ ] Create __init__.py exports

### Phase 2: Quality & Testing
- [ ] Setup pre-commit hooks
- [ ] Setup GitHub Actions CI
- [ ] Write unit tests
- [ ] Run quality checks
- [ ] Achieve >95% coverage

### Phase 3: Finalize
- [ ] Update main plan checklist
- [ ] Create comprehensive commit
- [ ] Create PR with detailed description

---

**End of Phase 1 Plan**
