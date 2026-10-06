const video = document.getElementById("movie-player");
const status = document.getElementById("player-status");
const retryButton = document.getElementById("stream-retry");

function showStatus(message) {
    status.textContent = message;
}

video.addEventListener("loadedmetadata", () => {
    showStatus("Video loaded. Press Play to start.");
});

video.addEventListener("error", () => {
    const error = video.error;
    const message = error?.code === MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED
        ? "This browser cannot decode this MKV or its HEVC video. Try a browser/device with MKV and HEVC support."
        : `The browser could not load the movie (media error ${error?.code ?? "unknown"}).`;
    showStatus(message);
    retryButton.hidden = false;
});

retryButton.addEventListener("click", () => {
    retryButton.hidden = true;
    video.load();
});
