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
**Target: 4 minutes 45 seconds | Maximum: 5 minutes**

## 2A. Architecture
**Time: 0:00–0:40**

**ON SCREEN**
1. Open the repository root in your editor.
2. Show the README architecture diagram.
3. Briefly point to the `frontend`, `backend`, and Docker configuration.

**SAY**

**"The application has two main parts. The frontend uses React, TypeScript, Vite, Tailwind CSS, and Recharts. The backend uses Python and FastAPI.**

**The backend handles the Elexon API requests, validates the data, and performs the forecast selection and accuracy calculations. The frontend displays the results.**

**We use Docker Compose to run both services together. Nginx serves the built frontend and routes API requests to the backend. The application does not need a database or user authentication for this pilot.**

**The deployment configuration also supports a separate frontend and hosted backend, using an API URL environment variable."**

## 2B. How we access Elexon data
**Time: 0:40–1:40**

**CODE TO OPEN BEFORE SPEAKING**
- `backend/app/elexon.py`, lines **1–39** — API behaviour and findings.
- Then `backend/app/main.py`, lines **88–98** — `windfor_window`.
- If time permits, `backend/app/elexon.py`, lines **54–94** — retries and errors.

**SAY**

**"One important part of the work was checking how the Elexon API behaves in practice, rather than relying only on the documentation.**

**The actual generation endpoint returns wind generation at half-hourly intervals. We filter the results to include only wind generation, and request data using the supported date parameters.**

**The forecast endpoint behaves differently. Its data is hourly, and each forecast has a publication time. We retrieve the relevant publication window, then select the forecast records we need in our backend.**

**This matters because the actuals and forecasts do not have the same time resolution. We handle that difference explicitly instead of treating the data as identical.**

**We also handle API errors. Permanent errors, such as invalid requests, are not retried. Temporary errors, such as rate limits or server failures, can be retried with a delay."**

## 2C. The most important logic — selecting the right forecast
**Time: 1:40–3:00**

**CODE TO OPEN BEFORE SPEAKING**
- `backend/app/logic.py`, lines **129–149** — `select_cutoff_forecast`.
- Then lines **57–66** — `parse_cutoff`.
- If needed, lines **86–127** — duplicate handling and record validation.
- Then lines **151–166** — latest-forecast selection.

**SAY**

**"This is the most important part of the assignment, because the forecast must be the one that was actually available when the buying decision was made.**

**For each half-hourly delivery interval, we find the matching hourly forecast, using the documented mapping that rounds the interval down to the hour. We then select the latest forecast published at or before the cutoff.**

**This check prevents us from using information that arrived too late. A forecast published after the decision time must not be included, even if it is more accurate.**

**We also handle the cutoff in London time, and convert it correctly using Python's timezone support. This avoids timezone mistakes when daylight saving time changes.**

**Duplicate records are handled consistently, and we keep missing values as missing instead of replacing them with zero. The latest available forecast is calculated separately from the cutoff forecast, so the two views cannot be confused."**

## 2D. Accuracy metrics and missing data
**Time: 3:00–4:00**

**CODE TO OPEN BEFORE SPEAKING**
- `backend/app/logic.py`, lines **230–259** — `compute_metrics`.
- Then lines **261–283** — percentile and uncertainty calculations.
- Open `frontend/src/views/Accuracy.tsx`, line **191** — `connectNulls={false}`.

**SAY**

**"Next, we calculate the forecast error and the accuracy metrics. Throughout the application, the signed error is forecast minus actual generation. A positive value means we overforecast, and a negative value means we underforecast.**

**MAE measures the average absolute error, while RMSE gives more weight to larger errors. We also calculate percentage-based metrics where they are meaningful. For MAPE, we exclude very small actual generation values to avoid misleading percentages.**

**If a metric cannot be calculated reliably, we return an unavailable value rather than showing zero. We also require enough observations before presenting the uncertainty percentiles.**

**On the frontend, missing daily results appear as gaps in the chart, not as zero values. This prevents the chart from suggesting that generation or error was zero when we actually had no valid data."**

## 2E. Tests, reliability, and next steps
**Time: 4:00–4:45**

**ON SCREEN**
1. Open `backend/tests/fixtures.py`.
2. Show the backend test files and test results.
3. Briefly show `backend/app/cache.py`, lines **22–33**.
4. Finish at the README, with the setup and deployment instructions visible.

**SAY**

**"We have 21 backend tests covering forecast cutoff selection, post-cutoff exclusion, duplicate records, timezone handling, metric calculations, and invalid API responses. The test fixtures are synthetic and clearly separated from live Elexon data.**

**The API validates user inputs and returns useful error messages. When the upstream service fails, the backend returns an appropriate error response instead of exposing a traceback.**

**We also cache API responses on disk for 24 hours, using the dataset and query parameters as the cache key. This reduces repeated requests and makes the application faster after the first load.**

**The next improvements would be more cutoff presets, a fully offline test mode, and completing the hosted deployment. The main goal was to build a clear, testable first version that handles forecast timing correctly and makes the results easy to review."**

---

# Final recording checklist

- [ ] Run `docker compose up --build`.
- [ ] Open `http://localhost:8080` and verify the charts and tabs work.
- [ ] Run `curl -s http://localhost:8000/api/health`.
- [ ] Check that all displayed metrics match the current application.
- [ ] Verify the specified file paths and line numbers in your current code.
- [ ] Do not describe the January dataset as real-time data. Say **real Elexon data for January 2026**.
- [ ] Confirm the public GitHub repository and deployed URL work in an incognito window.
- [ ] Record Part 1 and Part 2, keeping each under five minutes.
- [ ] Upload the video to YouTube as **Unlisted**, and verify the link in an incognito window.
- [ ] Include the video, repository, and deployed application links in the submission form.
