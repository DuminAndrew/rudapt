import Image from "next/image";
import Link from "next/link";

export function Logo({ size = 40 }: { size?: number }) {
  return (
    <Link href="/feed" className="flex items-center gap-3 group">
      <Image src="/logo.svg" alt="RuDapt" width={size * 3.3} height={size} priority />
    </Link>
  );
}
