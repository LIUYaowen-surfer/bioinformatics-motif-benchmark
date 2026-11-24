You are provided with target DNA sequences, local motif resources and a task specification in input/task.json.
Analyze the sequences using the specified background policy and ranking statistic. Identify the top 10 motifs in the required ID namespace. Use the available local tools; do not access the internet or external answer files.
Write result.json in the workspace root with exactly one key, "ids", containing exactly 10 unique motif-ID strings in ranked order. Preserve identifier spelling and case. Do not substitute TF gene IDs, synonyms or motif family names.
Write methods.md describing the commands, software/database versions, background model and ranking criterion. Do not confuse motif-to-motif similarity statistics with sequence or positional enrichment.
