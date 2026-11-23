# Conventional workflow evaluation report

**Source:** saved results in `eval - all features/` and `eval - feature selection/`.  
**Dataset split:** 455 development rows and 114 held-out test rows, stratified with split random state 42.  
**Repeated CV seeds:** 11, 42, and 67; 5 folds per seed.  
**Date of report:** 2026-11-22.

## Executive summary

- The all-features workflow selected **SVC** by mean development CV F1: **0.9614** (seed SD **0.0004**). The feature-selection workflow selected **XGB**: **0.9543** (SD **0.0067**). Across the paired seed-wise winners, feature selection was lower by **0.0066 F1** on average; the exact paired test was not significant (**p = 0.25**, n = 3).
- On the saved single test split, SVC with all features scored **Accuracy 0.9737, F1 0.9630, AUROC 0.9947**. Feature-selection XGB scored **0.9649, 0.9500, 0.9907**. This is a one-split descriptive comparison, not a statistical test.
- Nested feature selection took **355.39 seconds** of recorded CV runtime across the 15 model/seed combinations, versus **22.15 seconds** for all-features CV (**16.0-fold**). It assessed **2,250** outer-fold candidate configurations and recorded **11,325** CV fits, versus **75** fits for all-features CV.
- Pipeline selection was seed-sensitive: all-features chose SVC twice and LR once; feature selection chose LR, XGB, and SVC once each. With only three seeds, none of the paired comparisons can establish a statistically significant difference.

## A. Classification performance

The following are means across the three seed-specific five-fold CV runs. SD is the sample standard deviation across seeds. The 95% intervals use a two-sided t interval with 2 degrees of freedom; with n=3 they are wide and should be treated as rough uncertainty intervals, not as evidence of population-level generalization. AUROC intervals are not truncated at 1.0.

### All features

| Model | Accuracy mean (SD) | 95% CI | F1 mean (SD) | 95% CI | AUROC mean (SD) | 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| LR | 0.9714 (0.0022) | [0.9660, 0.9769] | 0.9610 (0.0031) | [0.9534, 0.9687] | 0.9946 (0.0012) | [0.9916, 0.9975] |
| SVC | 0.9714 (0.0000) | [0.9714, 0.9714] | **0.9614 (0.0004)** | [0.9605, 0.9624] | 0.9940 (0.0013) | [0.9907, 0.9974] |
| RF | 0.9575 (0.0063) | [0.9417, 0.9733] | 0.9429 (0.0078) | [0.9235, 0.9624] | 0.9875 (0.0029) | [0.9803, 0.9948] |
| GB | 0.9590 (0.0077) | [0.9398, 0.9781] | 0.9445 (0.0109) | [0.9174, 0.9715] | 0.9893 (0.0026) | [0.9828, 0.9957] |
| XGB | 0.9656 (0.0051) | [0.9530, 0.9782] | 0.9536 (0.0066) | [0.9371, 0.9701] | 0.9907 (0.0016) | [0.9867, 0.9947] |

### Feature selection

| Model | Accuracy mean (SD) | 95% CI | F1 mean (SD) | 95% CI | AUROC mean (SD) | 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| LR | 0.9656 (0.0063) | [0.9498, 0.9813] | 0.9534 (0.0082) | [0.9330, 0.9737] | **0.9946 (0.0015)** | [0.9909, 0.9983] |
| SVC | 0.9656 (0.0046) | [0.9542, 0.9769] | 0.9540 (0.0053) | [0.9409, 0.9670] | 0.9939 (0.0028) | [0.9870, 1.0008] |
| RF | 0.9546 (0.0089) | [0.9325, 0.9766] | 0.9386 (0.0118) | [0.9092, 0.9681] | 0.9870 (0.0028) | [0.9802, 0.9939] |
| GB | 0.9524 (0.0034) | [0.9440, 0.9607] | 0.9351 (0.0044) | [0.9243, 0.9460] | 0.9886 (0.0025) | [0.9825, 0.9948] |
| XGB | **0.9663 (0.0046)** | [0.9549, 0.9777] | **0.9543 (0.0067)** | [0.9376, 0.9711] | 0.9915 (0.0029) | [0.9843, 0.9987] |

The top mean F1 models are nearly tied with their nearest competitors: all-features SVC exceeds LR by **0.00039 F1**, while feature-selection XGB exceeds SVC by **0.00037 F1**. Those margins are much smaller than their seed-level uncertainty.

### Held-out test results

These persisted results are from one stratified 20% test split (72 class-0 and 42 class-1 observations). They are point estimates; no test-set SD or confidence interval is available in the saved artifacts.

| Selected workflow | Model | Accuracy | Precision | Recall | F1 | AUROC | Test confusion matrix (TN, FP; FN, TP) |
|---|---|---:|---:|---:|---:|---:|---|
| All features | SVC | 0.9737 | 1.0000 | 0.9286 | 0.9630 | 0.9947 | (72, 0; 3, 39) |
| Feature selection | XGB | 0.9649 | 1.0000 | 0.9048 | 0.9500 | 0.9907 | (72, 0; 4, 38) |

The test F1 difference is 0.0130, corresponding to one additional false negative for the feature-selection model on this test set. The saved artifacts do not contain per-observation predictions for both models, so a paired test such as McNemar's test cannot be computed from the available files. This single-split difference should not be interpreted as statistically significant.

## B. Efficiency and computational resources

Runtime below is the recorded CV runtime per model/seed run, averaged over the three seeds. It excludes dataset download and notebook startup. Feature-selection runtimes include the nested search over feature counts.

| Model | All-features CV sec, mean (SD) | Feature-selection CV sec, mean (SD) |
|---|---:|---:|
| LR | 0.233 (0.031) | 6.296 (4.766) |
| SVC | 0.220 (0.049) | 3.678 (0.486) |
| RF | 1.786 (0.096) | 28.641 (1.656) |
| GB | 2.941 (0.053) | 28.557 (0.674) |
| XGB | 2.203 (0.173) | 51.289 (1.206) |
| **Total of all 15 runs** | **22.15 sec** | **355.39 sec** |

| Workflow | Candidate/configuration evaluations | CV fits | Mean CV runtime total |
|---|---:|---:|---:|
| All features | 15 pipeline/seed evaluations | 75 | 22.15 sec |
| Feature selection | 2,250 outer-fold feature-count candidate evaluations | 11,325 | 355.39 sec |

For feature selection, each model/seed run records 150 outer-fold candidate evaluations and 755 fits: 30 possible feature counts across each of five outer folds, with inner five-fold grid search and a refit per outer fold. Across five models and three seeds this is 2,250 candidate evaluations and 11,325 fits. The all-features runs perform five CV fits for each of 15 model/seed combinations.

The final-development workflow record reports 0.0125 sec to fit and save/load times of 0.0048/0.0025 sec for the all-features SVC. The feature-selection XGB final search/fit took 10.3867 sec, with save/load 0.0098/0.0071 sec. The measured test-scoring wall times were 0.0408 sec and 0.0976 sec, respectively; recorded process CPU times were 0.0469 sec and 0.5625 sec. Final-workflow CPU times were 0.0156 sec and 3.8125 sec. CPU time can exceed wall time for multithreaded native estimators. These timings are machine- and load-dependent. Memory and GPU utilization were not recorded. Feature selection costs substantially more and did not produce a higher mean CV F1 or held-out test score in these results.

## C. Reproducibility and workflow consistency

Both workflows use the same stratified development/test partition (random state 42; 455/114 rows) and the same three CV seeds (11, 42, 67), allowing seed-paired comparisons. Each pipeline has 15 recorded repeated-run rows overall: five models times three seeds. The feature-selection CV is nested: the outer fold evaluates generalization while inner CV selects the number of features.

Model choice varied across seeds:

| Workflow | Seed 11 | Seed 42 | Seed 67 | Selection consistency |
|---|---|---|---|---|
| All features | SVC, F1 0.9616 | LR, F1 0.9640 | SVC, F1 0.9617 | SVC 2/3; LR 1/3 |
| Feature selection | LR, F1 0.9582 | XGB, F1 0.9615 | SVC, F1 0.9481 | Three different models, each 1/3 |

The all-features scores are relatively stable for SVC and LR. Feature-selection selection is less consistent, and its best selected model's F1 ranges from 0.9481 to 0.9615 across seeds. Within XGB's nested feature search, the selected feature count ranges from 19 to 30 across outer folds; the final full-development refit chose 28 of 30 features. Thus the feature-selection workflow does not yield a compact, consistently selected feature set in these runs.

### Paired significance tests and effect sizes

For each base model, I compared feature-selection against all-features results paired by the same seed. I used a two-sided exact sign-flip permutation test on the three paired seed differences and report paired Cohen's *d*<sub>z</sub> (mean paired difference divided by the sample SD of paired differences). Holm correction was applied separately across the five base-model comparisons for each metric. With only three pairs, the exact two-sided test has very coarse resolution; its minimum attainable p-value is 0.25. Effect sizes are highly unstable at this sample size.

Differences below are **feature selection minus all features**. Every Holm-adjusted p-value is 1.000; none of the differences is statistically significant at 0.05.

| Base model | Accuracy difference | d_z | exact p | F1 difference | d_z | exact p | AUROC difference | d_z | exact p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LR | -0.00586 | -0.873 | 0.500 | -0.00770 | -0.865 | 0.500 | +0.00003 | +0.030 | 1.000 |
| SVC | -0.00586 | -1.281 | 0.250 | -0.00746 | -1.340 | 0.250 | -0.00010 | -0.072 | 1.000 |
| RF | -0.00293 | -1.155 | 0.500 | -0.00430 | -1.066 | 0.500 | -0.00053 | -0.909 | 0.250 |
| GB | -0.00659 | -1.134 | 0.500 | -0.00934 | -1.225 | 0.250 | -0.00060 | -1.064 | 0.250 |
| XGB | +0.00073 | +0.577 | 1.000 | +0.00074 | +0.545 | 0.750 | +0.00076 | +0.443 | 0.750 |

Comparing each workflow's seed-wise selected winner gives mean F1 difference **-0.00656** (feature selection minus all features), paired *d*<sub>z</sub> **-1.066**, exact p **0.25**. This is exploratory because the winning model is reselected separately for each seed, and n=3 remains too small for a reliable significance claim.

## D. Failure and risk analysis

1. **Feature selection spends substantial compute for no observed gain.** It adds about 16 times the total CV runtime and 11,250 more recorded CV fits. Its best CV F1 (0.9543) trails the all-features best (0.9614), and its test F1 (0.9500) trails the all-features test F1 (0.9630). Paired tests are underpowered, so this is evidence of poor efficiency in this experiment, not proof that feature selection is generally harmful.
2. **Selection decisions are unstable.** Across the three seeds, feature selection selected three different model families. The all-features method also switched between SVC and LR. The small CV margin between the top model and runner-up does not justify a confident claim that one pipeline is intrinsically superior.
3. **Feature reduction is modest and fold-sensitive.** The final feature-selection fit keeps 28/30 features, while XGB outer folds chose between 19 and 30. The search incurs substantial cost while offering limited final dimensionality reduction.
4. **Test comparison cannot be paired inferentially from the current artifacts.** Only aggregate test metrics and confusion matrices are stored; per-case predictions/probability scores are absent. This prevents paired tests and per-case error overlap analysis.
5. **Metadata consistency was corrected in the saved results.** The test metrics and final workflow already showed that scoring completed, while `run_metadata.json` was stale. I updated both metadata files to `Test_Scored: true` and added a `Final_Test_Metrics_Path` field. The existing notebook scoring code remains unchanged.
6. **Runtime fields have different scopes.** CV runtime includes the evaluation procedure; final fit/save/load and test scoring are separate timing fields. Do not add these blindly or compare them as if they measured identical work. In particular, feature-selection final development time includes nested feature search, while all-features final fit is a single fit.

## Conclusion

On these saved runs, the all-features workflow is the stronger practical choice: it is much faster, its selected SVC has the highest repeated-CV F1, and it also has the better single-split test result. However, the seed-paired tests do **not** find statistically significant differences, and three seeds provide very low inferential power. The result supports preferring the simpler all-features workflow for this experiment while treating the performance ranking as provisional. A stronger comparison would require more repeated outer splits and saved per-example predictions, with model selection separated from final evaluation.

## Result files used

- `eval - all features/conventional_repeated_runs.csv`
- `eval - all features/all_pipelines_summary.csv`
- `eval - all features/conventional_seed_selections.csv`
- `eval - all features/conventional_final_test.csv`
- Corresponding files under `eval - feature selection/`
- Both folders' `best_pipeline_record.json`, `run_metadata.json`, `data_partition_manifest.json`, and `decision_consistency.csv`
