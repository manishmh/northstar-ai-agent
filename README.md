# WindSight — Video Recording Script
**Total target: 9 minutes 15 seconds | Maximum: 10 minutes**

**Recording rule:** Read the bold text naturally, do not rush. Follow each numbered instruction before speaking. When showing code, open the specified file and line range first, then explain only the relevant part.

---

# PART 1 — Customer Presentation
**Target: 4 minutes 30 seconds | Maximum: 5 minutes**

## 1A. Opening — The main question
**Time: 0:00–0:40**

**ON SCREEN**
1. Open `http://localhost:8080`.
2. Select the **Overview** tab.
3. Set the delivery date to **15 January 2026**.
4. Set the cutoff to **12:00**.
5. Wait for the chart and metric cards to load.

**SAY**

**"We built WindSight to answer one important question, what did the wind forecast show when your team had to make its buying decision, and how accurate was that forecast?**

**The application uses Elexon data for January 2026, and helps you understand what was known at decision time, how the forecast changed, and how much it differed from actual wind generation."**

## 1B. What the team knew before buying
**Time: 0:40–1:50 | Requirement 1: Forecast available at decision time**

**ON SCREEN**
1. Point to the delivery date and cutoff controls.
2. Point to the metric cards.
3. Move to the forecast-versus-actual chart.
4. Hover over a few points to show the values.

**SAY**

**"You can select any delivery date, and choose the time when the purchasing decision needs to be made. By default, we use noon on the previous day, London time. This is a stated assumption for the pilot, and you can change it to test other timings.**

**For 15 January, the average forecast was around 11.8 gigawatts, equivalent to about 282 gigawatt-hours across the day.**

**The completeness indicator tells you whether the data is complete, partial, or unavailable. This is important because we should never present an incomplete forecast as if we have the full picture.**

**In this chart, blue shows the forecast available at the selected cutoff, and green shows actual generation. You can see where the forecast was higher than the wind power that was actually generated."**

## 1C. How the forecast changed over time
**Time: 1:50–2:50 | Requirement 2: Forecast evolution**

**ON SCREEN**
1. Click the **Forecast Timeline** tab.
2. Keep the preselected period, **25**.
3. Point to the timeline, then the amber cutoff marker.
4. Point to the cutoff, latest forecast, and actual comparison cards.

**SAY**

**"This page shows how the forecast changed over time, before and after the purchasing cutoff.**

**For this interval, we have 24 forecast publications. Each point represents a forecast publication, so we can see how the prediction changed as new information became available.**

**The amber marker identifies the forecast selected at our decision cutoff, which is 11,351 megawatts. Forecasts published after this point were not available for that decision, so we keep them separate.**

**The latest forecast was 10,229 megawatts, while actual generation was 9,742 megawatts. The forecast moved closer to the actual value, but it still overestimated generation."**

## 1D. Measuring forecast accuracy
**Time: 2:50–3:50 | Requirements 3 and 4: Accuracy, error magnitude, and direction**

**ON SCREEN**
1. Click the **Accuracy Analysis** tab.
2. Select the full January date range.
3. Point to the completeness indicator and metric cards.
4. Show the error histogram and percentile cards.
5. Scroll to the largest-errors table.

**SAY**

**"Now let's look at the accuracy across the entire month. We matched all 1,488 half-hourly intervals, so the evaluation covers the full month.**

**The mean absolute error, or MAE, is around 2 gigawatts. This tells us the average size of the forecast error, without considering whether the forecast was too high or too low.**

**The bias is around plus 1.8 gigawatts. A positive bias means the forecasts were generally higher than actual generation, so the wind output was often overestimated.**

**The histogram shows how frequently different error sizes occurred. The percentile figures help us understand larger errors, which is useful when planning for uncertainty.**

**Finally, this table highlights the intervals with the largest errors, so the team can investigate where the forecast was least reliable."**

## 1E. What this means for procurement
**Time: 3:50–4:30**

**ON SCREEN**
1. Return to the **Overview** tab.
2. Scroll to the **Procurement Implications** panel.
3. Point to the explanation of overforecasting and underforecasting.

**SAY**

**"For procurement, the direction of the error matters. If we expect more wind power than we actually receive, we may need to buy more electricity from other sources than planned. If we underestimate wind generation, we may plan to buy more electricity than necessary.**

**WindSight makes these risks easier to understand, using the available forecast and actual generation data. We do not calculate a final purchasing requirement, because that would also need electricity demand and other supply information.**

**That is the goal of this pilot, to make forecast information clearer, measure its accuracy, and help the team understand the risks before making purchasing decisions."**

---

# PART 2 — Technical Review
**Target: 4 minutes 45 seconds | Hard limit: 5 minutes**

## 2A. Architecture
**Time: 0:00–0:40**

**ON SCREEN**
1. Open the repository root in your code editor.
2. Show the README architecture diagram.
3. Point to the `frontend`, `backend`, and Docker configuration.

**SAY**

**"The application has two main parts. The frontend uses React, TypeScript, Vite, Tailwind CSS, and Recharts. The backend uses Python and FastAPI.**

**The backend handles Elexon API requests, validates the data, and calculates forecast accuracy. The frontend displays the results in charts and metric cards.**

**We use Docker Compose to run both services together. Nginx serves the built frontend and routes API requests to the backend. For this pilot, we don't need a database or user authentication.**

**The frontend can also be configured to connect to a separately hosted backend using an API URL environment variable."**

---

## 2B. How we access Elexon data
**Time: 0:40–1:40**

**FILE: `backend/app/elexon.py`, lines 1–39 — API behaviour and findings**

**SAY**

**"One important part of the work was checking how the Elexon API behaves in practice, rather than relying only on the documentation.**

**The actual generation endpoint returns wind generation at half-hourly intervals. We filter the results to include only wind generation, and request data using the supported date parameters.**

**The forecast endpoint behaves differently. Its data is hourly, and each forecast has a publication time. We retrieve the relevant publication window, then select the forecast records we need in our backend.**

**This matters because the actuals and forecasts do not have the same time resolution. We handle that difference explicitly instead of treating the data as identical."**

**FILE: `backend/app/main.py`, lines 88–98 — `windfor_window`**

**SAY**

**"Here, we define the time window used to retrieve forecast publications. We fetch a wider window than the delivery date itself, so we can find forecasts published before the purchasing cutoff, including forecasts created earlier."**

**FILE: `backend/app/elexon.py`, lines 54–94 — retries and error handling**

**SAY**

**"We also handle API errors. Permanent errors, such as invalid requests, are not retried. Temporary errors, such as rate limits or server failures, can be retried with a delay. This makes the data-loading process more reliable."**

---

## 2C. Selecting the correct forecast
**Time: 1:40–3:00**

**FILE: `backend/app/logic.py`, lines 129–149 — `select_cutoff_forecast`**

**SAY**

**"This is the most important part of the assignment, because we need to show the forecast that was actually available when the purchasing decision was made.**

**For each half-hourly delivery interval, we find the matching hourly forecast, using the documented mapping that rounds the interval down to the hour. We then select the latest forecast published at or before the cutoff time.**

**This check prevents us from using information that arrived too late. A forecast published after the decision time must not be included, even if it is more accurate."**

**FILE: `backend/app/logic.py`, lines 57–66 — `parse_cutoff`**

**SAY**

**"We handle the cutoff using London local time, and convert it correctly with Python's timezone support. This is important because the UK changes between standard time and daylight saving time during the year."**

**FILE: `backend/app/logic.py`, lines 86–105 — duplicate handling**

**SAY**

**"We handle duplicate records consistently, so the same forecast is not counted more than once. When duplicate records compete, we use a deterministic rule to select the record."**

**FILE: `backend/app/logic.py`, lines 107–127 — record validation and missing values**

**SAY**

**"We also remove invalid records and keep missing values as missing, instead of replacing them with zero. This prevents missing data from being mistaken for actual zero generation."**

**FILE: `backend/app/logic.py`, lines 151–166 — latest-forecast selection**

**SAY**

**"The latest forecast is calculated separately from the cutoff forecast. This lets us show the newest available prediction while preserving the forecast that would have been available at the purchasing decision time."**

---

## 2D. Accuracy metrics and missing data
**Time: 3:00–4:00**

**FILE: `backend/app/logic.py`, lines 230–259 — `compute_metrics`**

**SAY**

**"Next, we calculate forecast errors and accuracy metrics. Throughout the application, the signed error is forecast minus actual generation. A positive value means we overforecast, and a negative value means we underforecast.**

**MAE measures the average size of the error, while RMSE gives more weight to larger errors. We also calculate percentage-based metrics where they are meaningful."**

**FILE: `backend/app/logic.py`, line 43 and line 242 — MAPE threshold and calculation**

**SAY**

**"For MAPE, we exclude very small actual generation values because percentage errors can become misleading when the actual value is close to zero. We also report how many values were excluded."**

**FILE: `backend/app/logic.py`, lines 261–283 — percentile and uncertainty calculations**

**SAY**

**"We calculate error percentiles to show how large forecast errors can become. However, we only show these uncertainty figures when there are enough observations. If there isn't enough data, we report that the result is unavailable instead of presenting an unreliable estimate."**

**FILE: `frontend/src/views/Accuracy.tsx`, line 191 — `connectNulls={false}`**

**SAY**

**"There is also an important detail in the frontend. Days with missing results appear as gaps in the chart, rather than zeros. This avoids giving the impression that the error was zero when we actually had no valid data."**

---

## 2E. Tests, reliability, and next steps
**Time: 4:00–4:45**

**FILE: `backend/tests/fixtures.py` — test data**

**SAY**

**"We use test fixtures to check the application with controlled data. These fixtures are synthetic, and are kept separate from the live Elexon data."**

**ON SCREEN: Show the backend test files and the latest test results.**

**SAY**

**"We have 21 backend tests covering forecast cutoff selection, excluding forecasts published too late, duplicate records, timezone handling, metric calculations, and invalid API responses."**

**FILE: `backend/app/main.py`, lines 55–86 — request validation and error responses**

**SAY**

**"The API validates user inputs and returns useful error messages. If the upstream service fails, the backend returns an appropriate error response instead of exposing a traceback to the user."**

**FILE: `backend/app/cache.py`, lines 22–33 — filesystem cache**

**SAY**

**"We cache API responses on disk for 24 hours, using the dataset and query parameters as the cache key. This reduces repeated requests and makes the application faster after the first load."**

**ON SCREEN: Return to the README and show the setup instructions and deployment configuration.**

**SAY**

**"The next improvements would be more cutoff presets, a fully offline test mode, and completing the hosted deployment. The goal was to build a clear and testable first version, with correct forecast timing and results that are easy to review."**


