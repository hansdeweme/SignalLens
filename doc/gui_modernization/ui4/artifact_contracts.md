# Artifact contracts

`artifact_models.py` supplies frozen, Qt-free ForensicArtifact and SpatialTransform values. A descriptor binds the session, invocation, result ID, analysis revision and source SHA-256 to a detector/key artifact ID. The artifact's own SHA-256 identifies its current bytes; paths alone never authorize a display. IDs such as `ela/ela_image_path` are local to this full investigation identity, not globally unique filenames.

Dimensions are encoded raster dimensions. Source orientation is explicit. Transform coefficients map source edge coordinates to artifact edge coordinates. No crop origins or padding are invented. Evidence and hypothesis references are immutable tuples copied from UI-1 structured records. Reliability may be absent; absence is displayed as “Not recorded.”

Availability is separate from registration. Independent inspection can remain available when the source is missing, while linked modes are disabled. E denotes corrupt, missing, rejected or untrusted output; D denotes structured or shared-output references. A is a verified identity grid; B contains spatial candidates, and only TRANSFORMABLE B entries have a demonstrated transform. UNKNOWN B entries never enable linked modes. C denotes non-spatial diagnostics.

Schema version 1 sidecars contain payloads and serialized descriptors, result ID and source hash. Existing run files are untouched. Sidecars are created exclusively, never overwritten. Stored sidecars are read only under a matching investigation manifest; saved content hashes detect later replacement. Decoder/hash failures produce unavailable descriptors. The existing 100 MP/2048 px bounded preview limits still apply.
