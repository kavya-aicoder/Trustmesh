import { api } from "./api";
import type { AssetsResponse } from "../types/api";

export async function getAssets(): Promise<AssetsResponse> {
  return api.get<AssetsResponse>("/assets/");
}