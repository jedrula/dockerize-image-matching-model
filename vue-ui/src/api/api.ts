import axios, { type AxiosProgressEvent } from "axios";

export const apiUrl = import.meta.env.VITE_API_BASE_URL;

const api = axios.create({
  baseURL: apiUrl,
});

export const findMatch = async (
  file: File,
  folder: string,
  onUploadProgress: (progressEvent: AxiosProgressEvent) => void
) => {
  const formData = new FormData();
  formData.append("image1", file);

  try {
    const response = await api.post(
      `/find_match?folder_path=${folder}`,
      formData,
      {
        onUploadProgress,
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error uploading file:", error);
    throw error;
  }
};

export const getBestMatchPreview = async (
  file: File,
  bestMatch: string,
  onUploadProgress: (progressEvent: AxiosProgressEvent) => void
) => {
  const formData = new FormData();
  formData.append("image1", file);

  try {
    const response = await api.post(
      `/get_matching_with?image_path=${encodeURIComponent(bestMatch)}`,
      formData,
      {
        responseType: "blob",
        onUploadProgress,
      }
    );
    return response;
  } catch (error) {
    console.error("Error fetching best match preview:", error);
    throw error;
  }
};

export const getMatchingMatrix = async (file1: File, file2: File) => {
  const formData = new FormData();
  formData.append("image1", file1);
  formData.append("image2", file2);

  try {
    const response = await api.post("/get_matching_matrix", formData);
    return response.data;
  } catch (error) {
    console.error("Error fetching matching matrix with files:", error);
    throw error;
  }
};
