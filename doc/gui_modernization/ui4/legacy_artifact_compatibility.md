# Stored-result compatibility

UI-1 import creates a fresh local session/result identity and retains historical investigation metadata. UI-4 resolves the original run directory from the imported report location, including report_revisions generations, without migrating it. A matching run-manifest result ID and source hash authorize paths under that directory. Legacy summaries without this identity retain their narrative and structured sections; image candidates remain explicitly untrusted/unavailable.

Existing section.artifacts paths support sensor/CFA/patch/compression/subject outputs. Known ELA/noise persisted JSON files recover their explicit fields. fft_results.json is accepted only if its input name matches the global prepared image: regional FFT calls overwrite the same filename. UI-4 never silently presents a regional spectrum as global output. Summary overlay_paths supplies compound boundary outputs for independent inspection.

New completed live sessions may create ui_artifacts_v1.json once, containing detached payloads and descriptors. Stored reopening checks its identity and saved hashes and uses it to recover payload-only artifacts. It never overwrites a sidecar or modifies original detector images, reports or summary files. Read-only or failed sidecar writes are reported without invalidating analysis results.

Older results can lack payload-only person-mask artifacts even when derived masks survive in summary details. Missing source bytes disable linked comparisons. If no artifact metadata survives, a structured/unavailable descriptor is shown; no basename search in another directory is attempted. Re-exported imports preserve narrative but may no longer be adjacent to the original artifacts; relocation remains an explicit limitation.
