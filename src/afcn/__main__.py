"""The aFCn program conducts haplotype analysis of gene expression.

By: Genomic Data Modeling Laboratory
"""

import sys
import os
import argparse
import logging


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument("--version",
                    dest="version",
                    action="store_true")

subparsers = parser.add_subparsers(title = "subcommands",
                                   dest = "subparser_name",
                                   help = "Select the task for afcn to complete.")


# ================================================================

# fit subcommand

# fit_parser = subparsers.add_parser(
#         "fit",
#         help="Fit gene expression effect sizes from phased genotypes.",
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         description="Fit model parameters and write to file in direcotry.",
#         epilog = """OUTPUT FILE SPECIFICATION
# """)
# 
# fit_parser.add_argument("--vcf", 
#                         type=str,
#                         required=True, 
#                         help="Genotype VCF file name")
# 
# fit_parser.add_argument("--expr", 
#                         type=str,
#                         required=True, 
#                         help="BED file containing 4 BED fields and "
#                             "gene expression per sample.")
# 
# 
# # optional inputs
# 
# fit_parser.add_argument("--eqtl", 
#                         type=str,
#                         default=None,
#                         help=("Name of file that contains eQTLs for which log "
#                               "allelic fold change values are inferred from "
#                               "data. The first and second columns must be "
#                               "#gene_id and variant_id, "
#                               "respectively (default None)"))
# 
# 
# # TODO write specification of covariate file
# 
# fit_parser.add_argument("--covariates",
#                         type=str,
#                         required=False,
#                         help=("File containing covariate data."))
# 
# fit_parser.add_argument("output_dir",
#                         type=str,
#                         nargs="?",
#                         default="afcs.bed", 
#                         help="Output file name")
# 

# ================================================================

# prediction subcommand

predict_parser = subparsers.add_parser(
        "predict",
        help="Predict gene expression from phased genotype data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Given an individual's cis-regulatory variant genotype
and log2 fold change effect sizes predict gene expression 
under the model by Mohammadi et al. Genome Research 2017.""",
        epilog = """
SPECIFICATION PARAMETER FILE INPUT

BED 4 file with meta data and header as follows:

* line [0, n): meta data prepended with ##
* line n: header prepended with #
* line [n+1, n+1+N_eqtls): records

Contents:

## meta data
    - ##afcn_version = (version str)
    - ##vcf_file = (str)
    - ##expression_file = (str)
    - ##eqtl_file = (str)
    - etc.
* BED fields labeled: 
    - #chrom, 
    - qtl_start: (int) minimum(variant position, gene position)
    - qtl_end: (int) maximum(variant position, gene position)
    - qtl_id: (string) gene_id/variant_id
* custom fields:
    - gene_start: (integer) start of genomic feature
    - gene_end: (integer) end of genomic feature
    - gene_id: (string) gene name
    - variant_pos: (integer) variant genomic coordinates from VCF
    - variant_id: (string)
    - ref: (char) reference allele
    - alt: (char) alternative allele
    - log2_afc: (float) estimated model parameter
    - remaining columns are statistics relevant to
        parameter inference


OUTPUT FILES

* <user_prefix>.bed
* <user_prefix>.log

default to
* predict.bed
* predict.log


SPECIFICATION predictions.bed

BED 4 file with meta data and header as follows:

* line [0, n): meta data prepended with ##
* line n: header prepended with #
* line [n+1, n+1+N_samples): records

Contents:

* meta data
    - ##afcn_version=(version str)
    - ##vcf_file=(str)
    - ##parameter_file=(str)
* BED fields labeled: 
    - #chrom, start, end, name
* custom fields:
    - sample_id: (float) predicted gene expression per sample
""")

predict_parser.add_argument(
        "--vcf",
        required=True,
        help="""VCF file version 4.4 as defined in the samtools 
        documentation.""")
predict_parser.add_argument(
        "--params",
       required=True,
       help="""Tab delimited text file providing
       log2 aFC point estimates per (gene, variant)
       pair.  See below for more details.
       """)
predict_parser.add_argument("--filters",
            default=["PASS"],
            type=str,
            nargs="+",
            help="""Filter(s) that genotypes must meet to be
                 included in the analysis.  Note that if you 
                 would like to include variants for which the VCF
                 filter value is '.', include 'missing' as a
                 filter value.  Input is not
                 case sensitive, default pass""")

predict_parser.add_argument(
        "-o",
        type=str,
        default=None,
        help=("File prefix, and path, for the results"
              " and log files"))

# ================================================================

# twas subcommand

twas_parser = subparsers.add_parser(
        "twas",
        help="""Perform transcriptome wide association study
        from gene expression predictions.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Given a set of gene expression predictions per individual, perform 
association tests between the predicted expression and a observed
phenotype.
""",
        epilog = """
OUTPUT FILE SPECIFICATION
""")

twas_parser.add_argument(
        "--pheno_column",
        default=None,
        type=int,
        help="# TODO")
twas_parser.add_argument(
        '--pheno_name',
        type=str,
        default=None,
        help="# TODO")

twas_parser.add_argument(
        "--filter_file",
        type=str,
        help="# TODO")
twas_parser.add_argument(
        '--filter_column',
        type=int,
        default=2)
twas_parser.add_argument(
        '--filter_val',
        type=int,
        default='1',
        help="# TODO")

twas_parser.add_argument(
        "--pred_exp_file",
        type=str,
        help="Predicted gene expression bed file",

twas_parser.add_argument(
        '--test_type',
        choices=["linear", "logistic"],
        default='linear')

twas_parser.add_argument(
        '--missing_phenotype',
        default=None,
        type=float)
twas_parser.add_argument(
    "--drop_nans",
    action="store_true",
    help="Should nans be dropped from phenotype table")
twas_parser.add_argument(
    "--out",
    type=str,
    help="Print association results to file.")



# ================================================================

# parse input


args = parser.parse_args(sys.argv[1:])

if args.o is None:
    args.o = args.subparser_name

logging.basicConfig(filename=f"{args.o}.log",
                level=logging.INFO,
                filemode="w",
                format="%(levelname)s\t%(asctime)s\t%(message)s",
                datefmt="%Y-%m-%d %H:%M:%S")
logging.info(" ".join(sys.argv))



if args.version:
    import afcn
    print(f"afcn {afcn.__version__}")

if args.subparser_name == "fit":
    from . import _fit

    _fit.run()


if args.subparser_name == "predict":
    from . import _predict
    _predict.run(args.vcf, args.params, args.o, args.filters)


if args.subparser_name == "twas":
    from . import _twas

    _twas.run(args.pheno_file, args.pheno_name,
              args.filter_file, args.filter_column, args.filter_val,
              args.pred_exp_file,
              args.test_type,
              args.missing_phenotype,
              args.drop_nans,
              args.out)
