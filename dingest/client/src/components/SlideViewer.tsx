import type { Slide } from "../types/document";

interface SlideViewerProps {
  slides: Slide[];
}

export const SlideViewer = ({ slides }: SlideViewerProps) => {
  return (
    <div className="viewer slide-viewer">
      {slides.map((slide) => (
        <div key={slide.slide_number} className="slide-card">
          <div className="slide-card__number">Slide {slide.slide_number}</div>
          {slide.title && <h3 className="slide-card__title">{slide.title}</h3>}
          <p className="slide-card__content">{slide.content}</p>
        </div>
      ))}
    </div>
  );
};
