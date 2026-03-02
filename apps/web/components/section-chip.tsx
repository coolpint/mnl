type SectionChipProps = {
  label: string;
};

export function SectionChip({ label }: SectionChipProps) {
  return <span className="section-chip">{label}</span>;
}

