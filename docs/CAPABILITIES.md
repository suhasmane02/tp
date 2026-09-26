# Capability and provenance policy

The application calls only official Google endpoints. Public discovery uses Data API `channels.list`, `playlistItems.list`, and batched `videos.list`; `search.list` is a one-time fallback when a supplied value is neither an ID nor a handle. Owner-only aggregates are queried through YouTube Analytics `reports.query` under `yt-analytics.readonly`; Reporting API remains optional because report/job availability is channel-specific.

Analytics reports are requested only after OAuth and only with documented metric/dimension combinations. The UI/API marks owner-only values unavailable until they are returned. Competitors are explicitly `PUBLIC DATA` and only have public metadata/count snapshots. Raw API data is provenance `DOCUMENTED_API`; feature calculations are `DERIVED`; a future explicit approximation must be `ESTIMATED`; unsupported values are `UNAVAILABLE`.

Quota is minimized with playlist pagination, video batches of 50, and scheduled incremental re-sync. The API's published quota accounting is not a live remaining-quota endpoint, so the dashboard reports the configured local budget and request ledger estimate, not a fabricated Google remainder.
