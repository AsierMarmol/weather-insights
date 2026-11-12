# Team roles

One owner builds each complete component, including its tests, documentation and fixes. Another member reviews it. Roles do not imply work or reviews have already happened. Phase 1 was completed by Asier and is not reassigned.

| Owner | Whole deliverables | Main files | Reviewer |
| --- | --- | --- | --- |
| Asier | Product rules, complete catalog and sources, API feasibility, shared specification; verify shared fetch/save; Searcher and integration; delivery | P2.1-P2.5, reference data, app.py/searcher.py, P4.1/P4.3, P5.5, P6.1/P6.3 | Gabriel; Christian for catalog/P2.4 |
| Alejandra | Domain models, catalog loader and persistence; model/storage acceptance | models.py, storage.py and tests; P3.1/P5.1 | Christian |
| Gabriel | Reusable JSON base/OpenWeather subclass, configuration, request/cache/save service and API acceptance | client.py, config.py, service.py and tests; P3.2/P5.2 | Alejandra |
| Christian | Common-window scoring, rankings, comparisons, all-preferences metrics and analytical acceptance | analytics.py and tests; P3.3/P5.3 | Selin |
| Selin | Complete interactive Dashboard/charts and UI acceptance; final clean-clone verification | dashboard.py and tests; P4.2/P4.4/P5.4/P6.2 | Asier for UI; Christian for clean clone |

## Dependencies and boundaries

Asier supplies the simple nine-column catalog and [P2.4 specification](PHASE2_SCOPE.md#p24-shared-data-and-calculation-specification); catalog content stays with him. Alejandra builds the data software, Gabriel the API/save service, Christian the analytical engine, and Selin the Dashboard. Do not split a CSV or component among several implementers.

After review, independent component work can use isolated synthetic test inputs. Live integration requires models/storage -> API/service -> analytical results -> UI. Asier's P2.5 uses the completed shared storage/service to verify a genuine fetch/save/readback; it creates no competing implementation. His foundation ownership remains, while the other members own real coding work.

Asier owns shared preferences/search state and application wiring. Selin's Dashboard (P4.4) keeps its own window/results state but uses the same service, cache, save path and analytical engine; neither UI duplicates scoring. Component defects normally return to their owner. For the authorized P5.5 integrated walkthrough, Asier implemented the shared-storage performance, configuration robustness and small UI fixes with OpenAI Codex; Gabriel reviews these cross-component changes. Original component ownership and authorship remain unchanged. Component tests/docs are written with the component; Phase 5 checks the integrated result rather than repeating all construction work.

## Working convention

Use the task prompt in the active phase with the actual requester, task ID and existing inputs. Keep the project car-only and follow [Phase 2](PHASE2_SCOPE.md) plus the [API contract](WEATHER_API_CONTRACT.md). Update affected steps when interfaces change, record real results/reviews and follow [plan maintenance](PROJECT_PHASES.md#plan-maintenance).

Use actual Git identities and actual AI attribution. Every member must make meaningful contributions and understand the application. A task assignment or generated prompt is not evidence of a contribution. Keep personal credentials local. No commit, push, review request or merge is implied by this role document.
