import type { Slide } from "../types/document";

interface SlideViewerProps {
  slides: Slide[];
  isEditing?: boolean;
  onSlideChange?: (
    index: number,
    field: "title" | "content",
    value: string
  ) => void;
}

export const SlideViewer = ({
  slides,
  isEditing,
  onSlideChange,
}: SlideViewerProps) => {
  return (
    <div className="viewer slide-viewer">
      {slides.map((slide, i) => (
        <div key={i} className="slide-card">
          <div className="slide-card__number">
            Slide {slide.slide_number}
          </div>

          {isEditing ? (
            <>
              <input
                className="edit-input"
                style={{
                  marginBottom: "12px",
                  fontWeight: "bold",
                }}
                value={slide.title || ""}
                onChange={(e) =>
                  onSlideChange?.(i, "title", e.target.value)
                }
                placeholder="Slide Title"
              />

              <textarea
                className="edit-textarea"
                value={slide.content}
                onChange={(e) =>
                  onSlideChange?.(i, "content", e.target.value)
                }
                placeholder="Slide Content"
              />
            </>
          ) : (
            <>
              {slide.title && (
                <h3 className="slide-card__title">
                  {slide.title}
                </h3>
              )}

              <p className="slide-card__content">
                {slide.content}
              </p>
            </>
          )}
        </div>
      ))}
    </div>
  );
};