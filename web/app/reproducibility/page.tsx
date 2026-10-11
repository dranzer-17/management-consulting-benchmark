import type { Metadata } from "next"
import { CodeBlock } from "@/components/code-block"
import { PageShell, PageTitle } from "@/components/page-shell"
import { REPO_URL, BASE_PATH } from "@/lib/site"

export const metadata: Metadata = { title: "Reproducibility", description: "How to rerun the analysis and the website from a clean checkout.", alternates: { canonical: `${BASE_PATH}/reproducibility` } }

const H = ({ children }: { children: string }) => <h2 className="mb-3 mt-12 text-2xl font-bold">{children}</h2>

export default function Reproducibility() {
  return (
    <PageShell>
      <PageTitle title="Rerun the analysis yourself">
        <p>Everything on this site is regenerated from the repository. These steps need no private knowledge.</p>
      </PageTitle>

      <H>1. Prerequisites</H>
      <ul className="prose-report list-disc space-y-1 pl-5 text-[16px]">
        <li>Python 3.14 (the versions in <code>requirements.txt</code> are pinned against it) and Node.js 20 or later.</li>
        <li>Internet access only for step 2 (re-downloading raw data). The committed raw extracts let you skip it.</li>
      </ul>

      <H>2. Obtain the data</H>
      <p className="prose-report text-[16px]">The repository includes the raw extracts used for the published numbers in <code>data/raw/</code>. To download them again from the public sources:</p>
      <CodeBlock>{`make ingest`}</CodeBlock>
      <p className="prose-report text-[16px]">This is slow, calls public APIs and can return slightly different totals if an agency has amended records. The Canadian contracts file is about 640 MB; <code>python -m src.ingest.canada_contracts path/to/contracts.csv</code> accepts a copy you have already downloaded.</p>

      <H>3. Set up the environment</H>
      <CodeBlock>{`git clone ${REPO_URL}.git
cd management-consulting-benchmark
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt`}</CodeBlock>

      <H>4. Run the pipeline</H>
      <CodeBlock>{`make reproduce   # clean, metrics, figures, sources, website data, validation`}</CodeBlock>

      <H>5. Run the validation and tests</H>
      <CodeBlock>{`make check       # data validation only
make test        # validation plus every registered claim`}</CodeBlock>

      <H>6. Regenerate charts and tables</H>
      <p className="prose-report text-[16px]">Tables are written to <code>outputs/tables/</code> and static charts to <code>outputs/figures/</code> by <code>make reproduce</code>. The website’s own charts are drawn from the exported JSON.</p>

      <H>7. Launch the website locally</H>
      <CodeBlock>{`cd web
npm install
npm run dev      # http://localhost:3000`}</CodeBlock>

      <H>8. Known limitations and manual steps</H>
      <ul className="prose-report list-disc space-y-2 pl-5 text-[16px]">
        <li><strong>Scale figures are hand-compiled.</strong> <code>data/manual/firm_scale_points.csv</code> is entered by hand from linked sources, so that step cannot be automated. Most McKinsey and Bain points are unverified.</li>
        <li><strong>One third-party mirror.</strong> H-1B and PERM extracts are read from a public Hugging Face mirror of Department of Labor files, which has not been re-checked against the originals.</li>
        <li><strong>Registry data drifts.</strong> Re-downloaded totals can differ slightly from the published ones.</li>
        <li><strong>Not covered:</strong> McKinsey’s website cannot be read by automated requests; the Power BI dashboard and slide deck are not built.</li>
      </ul>
    </PageShell>
  )
}
