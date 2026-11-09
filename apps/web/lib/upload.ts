// Picture upload helpers. The limits match the API (services/engine/confam_engine/ocr/imageio.py).

export const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"] as const;
export const MAX_BYTES = 5 * 1024 * 1024; // about 5 MB
export const MAX_SIDE = 1600; // longest side we send (the server reads at 1600); phone photos are shrunk to this first

export type Problem = "type" | "size" | "busy" | "off" | "down";

/** null if the file looks like a picture we accept, "type" if not. The server checks the real bytes again. */
export function checkFileType(file: { type: string; name: string }): "type" | null {
  if ((ACCEPTED_TYPES as readonly string[]).includes(file.type)) return null;
  if (file.type === "" && /\.(jpe?g|png|webp)$/i.test(file.name)) return null;
  return "type";
}

/** Only ever shrinks, and keeps the shape. */
export function fitSize(width: number, height: number, max = MAX_SIDE): { width: number; height: number } {
  const longest = Math.max(width, height);
  if (longest <= max) return { width, height };
  const scale = max / longest;
  return { width: Math.max(1, Math.round(width * scale)), height: Math.max(1, Math.round(height * scale)) };
}

export function problemFor(status: number): Problem {
  if (status === 413) return "size";
  if (status === 415) return "type";
  if (status === 429) return "busy";
  if (status === 503) return "off";
  return "down";
}

/** A picture pasted with Ctrl+V. Plain text is ignored so pasting into the text box still works. */
export function imageFromClipboard(items: DataTransferItemList | undefined | null): File | null {
  if (!items) return null;
  for (const item of Array.from(items)) {
    if (item.kind === "file" && item.type.startsWith("image/")) {
      const file = item.getAsFile();
      if (file) return file;
    }
  }
  return null;
}

/** Where the browser calls the API directly (photos can be larger than a serverless request allows). */
export function apiBase(): string {
  return (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
}

/** Shrink to MAX_SIDE and re-encode as JPEG, in the browser. Throws if the picture cannot be decoded. */
export async function shrink(file: Blob): Promise<Blob> {
  const bitmap = await createImageBitmap(file);
  const { width, height } = fitSize(bitmap.width, bitmap.height);
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("no canvas");
  ctx.fillStyle = "#fff"; // JPEG has no transparency
  ctx.fillRect(0, 0, width, height);
  ctx.drawImage(bitmap, 0, 0, width, height);
  bitmap.close();
  return await new Promise<Blob>((resolve, reject) =>
    canvas.toBlob((b) => (b ? resolve(b) : reject(new Error("encode failed"))), "image/jpeg", 0.9),
  );
}
